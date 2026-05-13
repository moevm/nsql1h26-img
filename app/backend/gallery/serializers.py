from rest_framework import serializers

from .models import Image


class ImageSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    author = serializers.CharField(source="author.id", read_only=True)
    author_username = serializers.ReadOnlyField(source="author.username")
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

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
            "likes_count",
            "is_liked",
        ]
        read_only_fields = ["image_format", "width", "height", "file_size_mb"]


class ImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["title", "description"]
