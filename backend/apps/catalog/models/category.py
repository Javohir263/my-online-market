"""
Category — self-referencing tree.

MPTT yoki treebeard ishlatmaymiz (oddiy parent FK + helpers yetadi MVP uchun).
Chuqurlik cheklash B6 da validatsiya orqali (max 3 level: root → sub → sub-sub).
"""

from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class CategoryManager(models.Manager):
    def roots(self):
        return self.filter(parent__isnull=True, is_active=True).order_by("order", "name")

    def active(self):
        return self.filter(is_active=True)


class Category(TimeStampedModel):
    """Mahsulot kategoriyasi (daraxt strukturasi)."""

    name = models.CharField(_("name"), max_length=120)
    slug = models.SlugField(
        _("slug"), max_length=140, unique=True, db_index=True
    )
    description = models.TextField(
        _("description"), blank=True, default=""
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        related_name="children",
        null=True,
        blank=True,
    )

    image = models.ImageField(
        _("image"), upload_to="categories/", blank=True, null=True
    )
    icon = models.CharField(
        _("icon name (lucide-react)"),
        max_length=60,
        blank=True,
        default="",
        help_text=_("Masalan: 'shopping-bag', 'smartphone'"),
    )

    order = models.PositiveIntegerField(_("display order"), default=0)
    is_active = models.BooleanField(_("active"), default=True, db_index=True)

    # Denormalized — Product yaratilganda/o'chirilganda yangilanadi (B5.7 da
    # signal/save hook qo'shilishi mumkin, lekin MVP'da on-demand recompute).
    products_count = models.PositiveIntegerField(
        _("products count (cached)"), default=0
    )

    objects = CategoryManager()

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ("order", "name")
        indexes = [
            models.Index(fields=["parent", "is_active", "order"]),
        ]

    def __str__(self) -> str:
        return self.name

    # --- Tree helpers ------------------------------------------------------
    @property
    def depth(self) -> int:
        """0 = root, 1 = sub, 2 = sub-sub. Bir nechta DB query — kerakli
        joyda cache qilamiz."""
        d = 0
        node = self
        while node.parent_id is not None:
            node = node.parent
            d += 1
            if d > 10:  # safety
                break
        return d

    def get_ancestors(self) -> list["Category"]:
        chain: list[Category] = []
        node = self.parent
        while node is not None:
            chain.append(node)
            node = node.parent
        return list(reversed(chain))

    def get_full_path(self) -> str:
        return " / ".join([c.name for c in self.get_ancestors()] + [self.name])
