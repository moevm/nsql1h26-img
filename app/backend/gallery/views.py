from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter

from logs.models import ActionType, Log

from .filters import ImageFilter
from .models import Image
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import ImageSerializer, ImageUpdateSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrReadOnly,
    ]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ImageFilter
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ImageUpdateSerializer
        return ImageSerializer

    def perform_create(self, serializer) -> None:
        instance = serializer.save(author=self.request.user)

        Log.objects.create(
            user=self.request.user,
            action=ActionType.CREATE,
            payload={
                "image_id": str(instance.id),
                "title": instance.title,
                "format": instance.image_format,
            },
        )

    def perform_update(self, serializer) -> None:
        instance = serializer.save()

        Log.objects.create(
            user=self.request.user,
            action=ActionType.UPDATE,
            payload={
                "image_id": str(instance.id),
                "title": instance.title,
                "description": instance.description,
            },
        )

    def perform_destroy(self, instance) -> None:
        payload = {
            "image_id": str(instance.id),
            "title": instance.title,
            "deleted_format": instance.image_format,
        }

        instance.delete()

        Log.objects.create(
            user=self.request.user, action=ActionType.DELETE, payload=payload
        )
