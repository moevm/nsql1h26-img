from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser

from .models import ActionType, Log
from .serializers import LogSerializer


class LogPagination(PageNumberPagination):
    page_size = 20


class LogListView(ListAPIView):
    serializer_class = LogSerializer
    permission_classes = [IsAdminUser]
    pagination_class = LogPagination

    def get_queryset(self):
        qs = Log.objects.select_related("user").all()

        action = self.request.query_params.get("action")
        if action:
            qs = qs.filter(action=action)

        username = self.request.query_params.get("username")
        if username:
            qs = qs.filter(user__username__icontains=username)

        date_from = self.request.query_params.get("date_from")
        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        date_to = self.request.query_params.get("date_to")
        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        return qs


class ActionTypeListView(ListAPIView):
    permission_classes = [IsAdminUser]

    def list(self, request, *args, **kwargs):
        from rest_framework.response import Response

        choices = [{"value": v, "label": label} for v, label in ActionType.choices]
        return Response(choices)
