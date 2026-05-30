"""
Review service layer.
"""

from __future__ import annotations

from django.db import transaction
from django.db.models import F

from apps.catalog.models import Product
from apps.orders.models import Order, OrderItem
from apps.reviews.models import HelpfulVote, Review

# Verified purchase qaysi statusdagi order'lar hisobga olinadi
VERIFIED_ORDER_STATUSES = (
    Order.Status.CONFIRMED,
    Order.Status.SHIPPED,
    Order.Status.DELIVERED,
)


def detect_verified_purchase(user, product) -> bool:
    """User shu product'ni avval buyurtma qilganmi (active statuslar)?"""
    return OrderItem.objects.filter(
        order__user=user,
        order__status__in=VERIFIED_ORDER_STATUSES,
        product=product,
    ).exists()


@transaction.atomic
def create_review(*, user, product, rating: int, title: str, content: str) -> Review:
    review = Review.objects.create(
        user=user,
        product=product,
        rating=rating,
        title=title,
        content=content,
        is_verified_purchase=detect_verified_purchase(user, product),
        status=Review.Status.PENDING,
    )
    return review


@transaction.atomic
def update_review(review: Review, *, rating: int | None = None, title: str | None = None, content: str | None = None) -> Review:
    fields: list[str] = []
    if rating is not None:
        review.rating = rating
        fields.append("rating")
    if title is not None:
        review.title = title
        fields.append("title")
    if content is not None:
        review.content = content
        fields.append("content")
    # Tahrir — qaytadan moderatsiyaga
    if fields:
        review.status = Review.Status.PENDING
        fields.append("status")
        review.save(update_fields=fields)
    return review


@transaction.atomic
def toggle_helpful(*, user, review: Review) -> tuple[bool, int]:
    """Foydali ovozni toggle qiladi. Returns (is_voted, new_count)."""
    existing = HelpfulVote.objects.filter(user=user, review=review).first()
    if existing:
        existing.delete()
        Review.objects.filter(pk=review.pk).update(
            helpful_count=F("helpful_count") - 1
        )
        review.refresh_from_db(fields=["helpful_count"])
        return (False, review.helpful_count)

    HelpfulVote.objects.create(user=user, review=review)
    Review.objects.filter(pk=review.pk).update(
        helpful_count=F("helpful_count") + 1
    )
    review.refresh_from_db(fields=["helpful_count"])
    return (True, review.helpful_count)


@transaction.atomic
def recompute_product_rating(product_id) -> None:
    """Product.ratings_avg / ratings_count'ni approved review'lardan qayta hisoblaydi."""
    from django.db.models import Avg, Count
    from decimal import Decimal

    stats = Review.objects.filter(
        product_id=product_id, status=Review.Status.APPROVED
    ).aggregate(avg=Avg("rating"), count=Count("id"))

    avg = stats["avg"] or 0
    count = stats["count"] or 0
    Product.objects.filter(pk=product_id).update(
        ratings_avg=Decimal(f"{avg:.2f}"),
        ratings_count=count,
    )
