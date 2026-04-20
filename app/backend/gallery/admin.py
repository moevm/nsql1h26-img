from django.contrib import admin

from logs.models import ActionType, Log

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
    exclude = ("author",)
    list_filter = ("image_format", "created_at")
    readonly_fields = ("image_format", "width", "height", "file_size_mb")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.author = request.user

        super().save_model(request, obj, form, change)

        action = ActionType.UPDATE if change else ActionType.CREATE
        Log.objects.create(
            user=request.user,
            action=action,
            payload={
                "source": "admin_panel",
                "image_id": str(obj.id),
                "title": obj.title,
            },
        )

    def delete_model(self, request, obj):
        Log.objects.create(
            user=request.user,
            action=ActionType.DELETE,
            payload={
                "source": "admin_panel",
                "image_id": str(obj.id),
                "title": obj.title,
            },
        )
        super().delete_model(request, obj)
