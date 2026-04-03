from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import SearchFilter

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
    search_fields = ["title"]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ImageUpdateSerializer
        return ImageSerializer

    def perform_create(self, serializer) -> None:
        serializer.save(author=self.request.user)
