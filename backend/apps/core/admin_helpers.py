"""
Admin helper mixins — image preview, currency formatting, etc.
"""

from __future__ import annotations

from django.utils.html import format_html


def image_thumb_html(image_url: str, size: int = 56) -> str:
    """Inline thumbnail HTML."""
    if not image_url:
        return format_html(
            '<div style="width:{}px;height:{}px;background:#efe5d5;'
            'border-radius:6px;display:flex;align-items:center;'
            'justify-content:center;color:#a08967;font-size:11px;">—</div>',
            size,
            size,
        )
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;'
        "object-fit:cover;border-radius:6px;"
        'box-shadow:0 1px 3px rgba(0,0,0,0.12);" />',
        image_url,
        size,
        size,
    )


class ImagePreviewMixin:
    """Admin mixin — adds `image_preview(obj)` callable.

    Implementing admin sets `image_field_name` ("image" by default).
    Add `"image_preview"` to list_display or readonly_fields.
    """

    image_field_name: str = "image"
    image_thumb_size: int = 56

    def image_preview(self, obj):  # noqa: D401
        field = getattr(obj, self.image_field_name, None)
        url = field.url if field else ""
        return image_thumb_html(url, self.image_thumb_size)

    image_preview.short_description = "Preview"  # type: ignore[attr-defined]
