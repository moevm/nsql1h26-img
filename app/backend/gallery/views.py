import datetime

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, Throttled
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

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        _search_params = {
            "search",
            "author",
            "date_from",
            "date_to",
            "image_format",
            "min_size_mb",
            "max_size_mb",
            "min_width",
            "max_width",
            "min_height",
            "max_height",
        }
        active_search = {
            k: v for k, v in request.query_params.items() if k in _search_params
        }
        if active_search and request.user.is_authenticated:
            results_count = (
                response.data.get("count", len(response.data))
                if isinstance(response.data, dict)
                else len(response.data)
            )

            search_query = active_search.pop("search", None)
            Log.add_log(
                user=request.user,
                action=ActionType.SEARCH_EXECUTED,
                payload={
                    "query": search_query or "",
                    "filters": active_search,
                    "results_count": results_count,
                },
            )

        return response

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
            Log.add_log(
                user=request.user,
                action=ActionType.IMAGE_UNLIKED,
                payload={
                    "image_id": str(image.id),
                    "title": image.title,
                },
            )
        else:
            liked = True
            Log.add_log(
                user=request.user,
                action=ActionType.IMAGE_LIKED,
                payload={
                    "image_id": str(image.id),
                    "title": image.title,
                },
            )
        return Response(
            {"liked": liked, "likes_count": image.likes.count()},
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer) -> None:
        user = self.request.user

        if not user.is_staff:
            if user.publish_blocked:
                raise PermissionDenied("Возможность публикаций была ограничена.")

            now = timezone.now()
            hourly_count = Log.objects.filter(
                user=user,
                action=ActionType.IMAGE_UPLOADED,
                created_at__gte=now - datetime.timedelta(hours=1),
            ).count()
            if hourly_count >= user.hourly_post_limit:
                raise Throttled(
                    detail="Превышен часовой лимит публикаций. Попробуйте позже."
                )

            daily_count = Log.objects.filter(
                user=user,
                action=ActionType.IMAGE_UPLOADED,
                created_at__gte=now - datetime.timedelta(days=1),
            ).count()
            if daily_count >= user.daily_post_limit:
                raise Throttled(
                    detail="Превышен суточный лимит публикаций. Попробуйте позже."
                )

        instance = serializer.save(author=user)

        Log.add_log(
            user=user,
            action=ActionType.IMAGE_UPLOADED,
            payload={
                "image_id": str(instance.id),
                "title": instance.title,
                "file_path": instance.file.name if instance.file else "",
                "image_format": instance.image_format,
                "file_size_mb": instance.file_size_mb,
            },
        )

    def perform_update(self, serializer) -> None:
        old_instance = self.get_object()
        old_title = old_instance.title
        old_description = old_instance.description

        instance = serializer.save()

        changes = {}
        if old_title != instance.title:
            changes["title"] = {"old": old_title, "new": instance.title}
        if old_description != instance.description:
            changes["description"] = {
                "old": old_description,
                "new": instance.description,
            }

        if changes:
            Log.add_log(
                user=self.request.user,
                action=ActionType.METADATA_UPDATED,
                payload={"image_id": str(instance.id), "changes": changes},
            )

    def perform_destroy(self, instance) -> None:
        payload = {
            "image_id": str(instance.id),
            "title": instance.title,
            "file_path": instance.file.name if instance.file else "",
            "file_size_mb": instance.file_size_mb,
        }

        instance.delete()

        Log.add_log(
            user=self.request.user,
            action=ActionType.IMAGE_DELETED,
            payload=payload,
        )
