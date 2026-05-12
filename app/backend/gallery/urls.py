from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .stats_views import StatisticsView
from .views import ImageViewSet

router = DefaultRouter()
router.register(r"images", ImageViewSet, basename="image")

urlpatterns = [
    path("stats/", StatisticsView.as_view(), name="image-stats"),
    path("", include(router.urls)),
]
