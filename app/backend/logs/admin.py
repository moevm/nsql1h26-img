from django.contrib import admin

from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ("action", "user", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "payload")
    readonly_fields = ("user", "action", "payload", "created_at")
