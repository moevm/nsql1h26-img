from django.contrib import admin

from .models import Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "image_format",
        "file_size_mb",
        "width",
        "height",
        "author",
    )
    list_filter = ("image_format", "created_at")
    readonly_fields = ("image_format", "width", "height", "file_size_mb")
