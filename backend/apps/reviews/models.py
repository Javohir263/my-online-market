"""
Review + ReviewImage + HelpfulVote.

UNIQUE(product, user) — bir foydalanuvchi bitta mahsulot uchun bitta review yozadi.
"""

from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Review(TimeStampedModel):
    """Mahsulot uchun foydalanuvchi sharhi."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending review")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    rating = models.PositiveSmallIntegerField(
        _("rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    title = models.CharField(_("title"), max_length=140, blank=True, default="")
    content = models.TextField(_("content"))

    is_verified_purchase = models.BooleanField(
        _("verified purchase"),
        default=False,
        help_text=_(
            "Avtomatik o'rnatiladi — agar foydalanuvchi shu mahsulotni "
            "haqiqatda buyurtma qilgan bo'lsa."
        ),
    )
    helpful_count = models.PositiveIntegerField(
        _("helpful count"), default=0
    )

    status = models.CharField(
        _("moderation status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    rejected_reason = models.CharField(
        _("rejected reason"), max_length=255, blank=True, default=""
    )

    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="review_unique_product_user",
            ),
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="review_rating_range",
            ),
        ]
        indexes = [
            models.Index(fields=["product", "status", "-created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} → {self.product.name} ({self.rating}★)"


class ReviewImage(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(_("image"), upload_to="reviews/")
    order = models.PositiveIntegerField(_("order"), default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("review image")
        verbose_name_plural = _("review images")
        ordering = ("order", "id")

    def __str__(self) -> str:
        return f"Image for review #{self.review_id}"


class HelpfulVote(models.Model):
    """Foydalanuvchi review'ga 'foydali' deb ovoz beradi.

    UNIQUE(user, review) — bir kishi bir review'ga bir martagina ovoz.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="helpful_votes",
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="votes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("helpful vote")
        verbose_name_plural = _("helpful votes")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "review"],
                name="helpful_vote_unique_user_review",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} ♥ review #{self.review_id}"
