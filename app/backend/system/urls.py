from django.urls import path

from .views import SystemExportView, SystemImportView

urlpatterns = [
    path("backup/export/", SystemExportView.as_view(), name="system-export"),
    path("backup/import/", SystemImportView.as_view(), name="system-import"),
]
