import os

from django.conf import settings
from django.db import models


class Image(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.ImageField(
        upload_to="uploads/%Y/%m/%d/", width_field="width", height_field="height"
    )

    image_format = models.CharField(max_length=10, blank=True)
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    file_size_mb = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="images"
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if self.file:
            self.file_size_mb = round(self.file.size / (1024 * 1024), 3)
            ext = os.path.splitext(self.file.name)[1].lower().replace(".", "")
            self.image_format = ext.upper()

        super().save(*args, **kwargs)
