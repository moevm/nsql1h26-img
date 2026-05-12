from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from logs.models import ActionType, Log

from .filters import ImageFilter
from .models import Image, Like
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import ImageSerializer, ImageUpdateSerializer


class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrReadOnly,
    ]

    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ImageFilter
    search_fields = ["title", "description"]

    def get_queryset(self):
        qs = Image.objects.all()
        if (
            self.action == "list"
            and self.request.query_params.get("liked_by_me") == "true"
            and self.request.user.is_authenticated
        ):
            liked_image_ids = Like.objects.filter(user=self.request.user).values_list(
                "image_id", flat=True
            )
            qs = qs.filter(id__in=list(liked_image_ids))
        return qs

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return ImageUpdateSerializer
        return ImageSerializer

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def like(self, request, pk=None):
        image = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, image=image)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True
        return Response(
            {"liked": liked, "likes_count": image.likes.count()},
            status=status.HTTP_200_OK,
        )

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
