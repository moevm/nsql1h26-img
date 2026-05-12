from django.contrib import admin

from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("user", "action", "payload", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
