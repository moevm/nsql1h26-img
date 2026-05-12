from collections import defaultdict

from django.db.models import Count as DbCount
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from logs.models import ActionType, Log

from .filters import ImageFilter
from .models import Image

VALID_X_AXES = {"month", "day", "year", "image_format", "megapixels"}
VALID_METRICS = {
    "count",
    "total_size_mb",
    "avg_size_mb",
    "total_megapixels",
    "likes_count",
}  # noqa: E501

X_AXIS_LABELS = {
    "month": "Месяц",
    "day": "День",
    "year": "Год",
    "image_format": "Формат изображения",
    "megapixels": "Размер (МП)",
}

METRIC_LABELS = {
    "count": "Количество загрузок",
    "total_size_mb": "Суммарный объём (МБ)",
    "avg_size_mb": "Средний объём (МБ)",
    "total_megapixels": "Суммарный размер (МП)",
    "likes_count": "Количество лайков",
}


def _x_sort_key(x_key: str, display: str):
    """Return a sort key for the given display value so results are ordered sensibly."""
    if x_key == "month":
        # display is "2024-03" → sorts lexicographically == chronologically
        return display
    if x_key == "day":
        # display is "DD.MM.YYYY" — convert to sortable "YYYY-MM-DD"
        try:
            d, m, y = display.split(".")
            return f"{y}-{m}-{d}"
        except ValueError:
            return display
    if x_key == "megapixels":
        # display is "1.5 МП" → extract float
        try:
            return float(display.split()[0])
        except ValueError, IndexError:
            return 0.0
    return display


def _get_x_display(image: Image, x_key: str) -> str:
    if x_key == "month":
        return image.created_at.strftime("%Y-%m")
    if x_key == "day":
        return image.created_at.strftime("%d.%m.%Y")
    if x_key == "year":
        return image.created_at.strftime("%Y")
    if x_key == "image_format":
        return image.image_format or "—"
    if x_key == "megapixels":
        if image.width and image.height:
            mp = round(image.width * image.height / 1_000_000, 1)
            return f"{mp} МП"
        return "—"
    return "—"


def _compute_metric(images_in_group: list, metric: str) -> float:
    if metric == "count":
        return len(images_in_group)
    if metric == "total_size_mb":
        return round(sum(img.file_size_mb or 0 for img in images_in_group), 2)
    if metric == "avg_size_mb":
        sizes = [img.file_size_mb or 0 for img in images_in_group]
        return round(sum(sizes) / len(sizes), 2) if sizes else 0
    if metric == "total_megapixels":
        total = sum(
            (img.width or 0) * (img.height or 0) / 1_000_000 for img in images_in_group
        )
        return round(total, 2)
    if metric == "likes_count":
        return sum(getattr(img, "likes_count", 0) for img in images_in_group)
    return 0


def _apply_filters(request: Request):
    from django.db.models import Q

    qs = Image.objects.all()
    f = ImageFilter(request.query_params, queryset=qs)
    qs = f.qs

    search = request.query_params.get("search", "").strip()
    if search:
        qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

    return qs


class StatisticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> Response:
        x_key = request.query_params.get("x_axis", "month")
        metric = request.query_params.get("metric", "count")

        if x_key not in VALID_X_AXES:
            return Response({"detail": "Invalid x_axis value."}, status=400)
        if metric not in VALID_METRICS:
            return Response({"detail": "Invalid metric value."}, status=400)

        qs = _apply_filters(request)

        if metric == "likes_count":
            qs = qs.annotate(likes_count=DbCount("likes"))

        groups: dict[str, list] = defaultdict(list)
        for image in qs:
            label = _get_x_display(image, x_key)
            groups[label].append(image)

        sorted_labels = sorted(groups.keys(), key=lambda lbl: _x_sort_key(x_key, lbl))

        labels = []
        data = []
        for lbl in sorted_labels:
            labels.append(lbl)
            data.append(_compute_metric(groups[lbl], metric))

        query_params = request.query_params.dict()
        query_params.pop("x_axis", None)
        query_params.pop("metric", None)
        search = query_params.pop("search", "")

        Log.add_log(
            user=request.user,
            action=ActionType.STATS_VIEWED,
            payload={
                "x_axis": x_key,
                "metric": metric,
                "search": search,
                "filters": query_params,
                "groups_count": len(labels),
                "analyzed_images_count": sum(len(g) for g in groups.values()),
            },
        )

        return Response(
            {
                "labels": labels,
                "data": data,
                "x_label": X_AXIS_LABELS[x_key],
                "metric_label": METRIC_LABELS[metric],
            }
        )
