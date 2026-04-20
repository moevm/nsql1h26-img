from rest_framework import serializers

from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    author = serializers.CharField(source="author.id", read_only=True)
    author_username = serializers.ReadOnlyField(source="author.username")

    class Meta:
        model = Image
        fields = [
            "id",
            "title",
            "description",
            "file",
            "image_format",
            "width",
            "height",
            "file_size_mb",
            "created_at",
            "updated_at",
            "author",
            "author_username",
        ]
        read_only_fields = ["image_format", "width", "height", "file_size_mb"]


class ImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["title", "description"]
