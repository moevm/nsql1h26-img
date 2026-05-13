from django.urls import path

from .views import ActionTypeListView, LogListView

urlpatterns = [
    path("logs/", LogListView.as_view(), name="log-list"),
    path("logs/action-types/", ActionTypeListView.as_view(), name="log-action-types"),
]
