from django.conf import settings
from django.db import models


class ActionType(models.TextChoices):
    USER_REGISTERED = "user_registered", "Регистрация пользователя"
    USER_LOGGED_IN = "user_logged_in", "Вход в систему"
    USER_LOGGED_OUT = "user_logged_out", "Выход из системы"
    PASSWORD_CHANGED = "password_changed", "Изменение пароля"
    PASSWORD_RECOVERED = "password_recovered", "Восстановление пароля"

    IMAGE_UPLOADED = "image_uploaded", "Загрузка изображения"
    METADATA_UPDATED = "metadata_updated", "Обновление метаданных"
    IMAGE_DELETED = "image_deleted", "Удаление изображения"

    SEARCH_EXECUTED = "search_executed", "Выполнение поиска"
    STATS_VIEWED = "stats_viewed", "Просмотр статистики системы"

    DATABASE_EXPORTED = "database_exported", "Экспорт базы данных"
    DATABASE_IMPORTED = "database_imported", "Импорт базы данных"


class Log(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="action_logs",
    )
    action = models.CharField(max_length=50, choices=ActionType.choices)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        username = self.user.username if self.user else "System/Deleted User"
        date_str = self.created_at.strftime("%Y-%m-%d %H:%M")
        return f"[{self.action}] {username} - {date_str}"

    @classmethod
    def add_log(cls, user, action, payload=None):
        return cls.objects.create(
            user=user if user and getattr(user, "is_authenticated", False) else None,
            action=action,
            payload=payload or {},
        )
