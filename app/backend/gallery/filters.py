import django_filters
from django.db.models import QuerySet

from .models import Image


class ImageFilter(django_filters.FilterSet):
    author = django_filters.CharFilter(
        field_name="author__username", lookup_expr="icontains"
    )
    date_from = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    date_to = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    image_format = django_filters.CharFilter(method="filter_multiple_formats")
    min_size_mb = django_filters.NumberFilter(
        field_name="file_size_mb", lookup_expr="gte"
    )
    max_size_mb = django_filters.NumberFilter(
        field_name="file_size_mb", lookup_expr="lte"
    )
    min_width = django_filters.NumberFilter(field_name="width", lookup_expr="gte")
    max_width = django_filters.NumberFilter(field_name="width", lookup_expr="lte")
    min_height = django_filters.NumberFilter(field_name="height", lookup_expr="gte")
    max_height = django_filters.NumberFilter(field_name="height", lookup_expr="lte")

    class Meta:
        model = Image
        fields = []

    def filter_multiple_formats(
        self, queryset: QuerySet, name: str, value: str
    ) -> QuerySet:
        formats_list = [fmt.strip().upper() for fmt in value.split(",") if fmt.strip()]
        return queryset.filter(image_format__in=formats_list)
