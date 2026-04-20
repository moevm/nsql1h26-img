from django.conf import settings
from django.db import models


class ActionType(models.TextChoices):
    CREATE = "CREATE", "Создание"
    UPDATE = "UPDATE", "Обновление"
    DELETE = "DELETE", "Удаление"


class Log(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_logs",
    )
    action = models.CharField(max_length=20, choices=ActionType.choices)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        username = self.user.username if self.user else "System/Deleted User"
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"[{self.action}] {username} - {date_str}"
