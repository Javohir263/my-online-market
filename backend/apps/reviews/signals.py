"""
Reviews signals — Product.ratings_avg/count denorm yangilanishi.

post_save (status APPROVED yoki keldi/ketdi) va post_delete uchun.
"""

from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.reviews.models import Review
from apps.reviews.services import recompute_product_rating


@receiver(post_save, sender=Review)
def review_saved(sender, instance: Review, created: bool, **kwargs) -> None:
    """Status APPROVED bo'lganda yoki APPROVED edi → boshqaga (rejected/pending)
    o'tganda, product rating qayta hisoblanadi."""
    recompute_product_rating(instance.product_id)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance: Review, **kwargs) -> None:
    recompute_product_rating(instance.product_id)
