"""
Product family — Product + ProductImage + ProductVariant + ProductAttribute.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel, UUIDModel

from .brand import Brand
from .category import Category
from .tag import ProductTag


# =============================================================================
# Product
# =============================================================================
class Product(UUIDModel, TimeStampedModel):
    """Asosiy mahsulot modeli. UUID id (public-facing, sequential leak yo'q)."""

    DEFAULT_CURRENCY = "UZS"

    # --- Foreign relations ---
    vendor = models.ForeignKey(
        "vendors.Vendor",
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        db_index=True,
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        related_name="products",
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(
        ProductTag, related_name="products", blank=True
    )

    # --- Identifiers ---
    slug = models.SlugField(
        _("slug"), max_length=200, unique=True, db_index=True
    )
    sku = models.CharField(
        _("SKU"),
        max_length=64,
        unique=True,
        db_index=True,
        help_text=_("Stock Keeping Unit — unique product code"),
    )

    # --- Translated content ---
    name = models.CharField(_("name"), max_length=200)
    short_description = models.CharField(
        _("short description"), max_length=500, blank=True, default=""
    )
    description = models.TextField(_("description"), blank=True, default="")

    # --- Pricing ---
    currency = models.CharField(
        _("currency"), max_length=3, default=DEFAULT_CURRENCY
    )
    base_price = models.DecimalField(
        _("base price"),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )
    sale_price = models.DecimalField(
        _("sale price"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text=_("Agar chegirma bo'lsa — base_price'dan kichik."),
    )

    # --- Inventory ---
    stock_quantity = models.PositiveIntegerField(
        _("stock quantity"), default=0
    )
    is_in_stock = models.BooleanField(
        _("in stock"), default=True, db_index=True
    )

    # --- Denormalized counters (yangilanadi signal/service tomonidan) ---
    ratings_avg = models.DecimalField(
        _("ratings avg"),
        max_digits=3,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
            MaxValueValidator(Decimal("5.00")),
        ],
    )
    ratings_count = models.PositiveIntegerField(
        _("ratings count"), default=0
    )
    views_count = models.BigIntegerField(_("views count"), default=0)

    # --- Flags ---
    is_active = models.BooleanField(_("active"), default=True, db_index=True)
    is_featured = models.BooleanField(_("featured"), default=False)
    is_new = models.BooleanField(_("new arrival"), default=False)
    is_bestseller = models.BooleanField(_("bestseller"), default=False)

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=["category", "is_active", "-created_at"],
                name="product_cat_active_idx",
            ),
            models.Index(
                fields=["vendor", "is_active"], name="product_vendor_idx"
            ),
            models.Index(
                fields=["is_featured", "is_active"],
                name="product_featured_idx",
            ),
            models.Index(
                fields=["is_active", "-ratings_avg"],
                name="product_rated_idx",
            ),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(sale_price__isnull=True)
                    | Q(sale_price__lte=models.F("base_price"))
                ),
                name="product_sale_lte_base",
            ),
            models.CheckConstraint(
                condition=Q(ratings_avg__gte=0) & Q(ratings_avg__lte=5),
                name="product_ratings_avg_range",
            ),
        ]

    def __str__(self) -> str:
        return self.name

    # --- Price helpers -----------------------------------------------------
    @property
    def current_price(self) -> Decimal:
        if self.sale_price is not None and self.sale_price < self.base_price:
            return self.sale_price
        return self.base_price

    @property
    def has_discount(self) -> bool:
        return (
            self.sale_price is not None and self.sale_price < self.base_price
        )

    @property
    def discount_percentage(self) -> int:
        if not self.has_discount or self.base_price <= 0:
            return 0
        discount = (self.base_price - self.sale_price) / self.base_price
        return int(discount * 100)

    # --- Stock helpers -----------------------------------------------------
    def sync_stock_flag(self, save: bool = True) -> None:
        new_value = self.stock_quantity > 0
        if new_value != self.is_in_stock:
            self.is_in_stock = new_value
            if save:
                self.save(update_fields=["is_in_stock"])


# =============================================================================
# ProductImage
# =============================================================================
class ProductImage(TimeStampedModel):
    """Mahsulot rasmi. Cloudinary'da saqlanadi (production'da)."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(_("image"), upload_to="products/")
    alt_text = models.CharField(
        _("alt text"), max_length=200, blank=True, default=""
    )
    order = models.PositiveIntegerField(_("order"), default=0)
    is_primary = models.BooleanField(_("primary"), default=False)

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")
        ordering = ("-is_primary", "order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="product_image_one_primary",
            ),
        ]
        indexes = [
            models.Index(fields=["product", "order"]),
        ]

    def __str__(self) -> str:
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs) -> None:
        """Yangi primary o'rnatilganda eskisini avtomatik unset qilish."""
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


# =============================================================================
# ProductVariant
# =============================================================================
class ProductVariant(TimeStampedModel):
    """Mahsulot variantasi (rang, o'lcham). SKU har biri uchun unique."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    sku = models.CharField(
        _("variant SKU"), max_length=64, unique=True, db_index=True
    )
    color = models.CharField(_("color"), max_length=60, blank=True, default="")
    size = models.CharField(_("size"), max_length=40, blank=True, default="")
    additional_price = models.DecimalField(
        _("additional price"),
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=_("Variant uchun base_price'ga qo'shiladi (yoki ayriladi)"),
    )
    stock_quantity = models.PositiveIntegerField(
        _("stock quantity"), default=0
    )
    image = models.ImageField(
        _("variant image"),
        upload_to="products/variants/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        verbose_name = _("product variant")
        verbose_name_plural = _("product variants")
        ordering = ("product", "color", "size")
        indexes = [
            models.Index(fields=["product", "is_active"]),
        ]

    def __str__(self) -> str:
        bits = [self.product.name]
        if self.color:
            bits.append(self.color)
        if self.size:
            bits.append(self.size)
        return " — ".join(bits)

    @property
    def final_price(self) -> Decimal:
        return self.product.current_price + self.additional_price


# =============================================================================
# ProductAttribute
# =============================================================================
class ProductAttribute(TimeStampedModel):
    """Mahsulot xususiyatlari ("Material: Cotton", "Weight: 200g")."""

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="attributes"
    )
    name = models.CharField(_("attribute name"), max_length=80)
    value = models.CharField(_("attribute value"), max_length=200)
    order = models.PositiveIntegerField(_("order"), default=0)

    class Meta:
        verbose_name = _("product attribute")
        verbose_name_plural = _("product attributes")
        ordering = ("product", "order", "name")
        indexes = [
            models.Index(fields=["product", "order"]),
        ]

    def __str__(self) -> str:
        return f"{self.name}: {self.value}"
