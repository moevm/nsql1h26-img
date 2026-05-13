from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("user", "User"),
        ("admin", "Admin"),
    )

    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default="user")
    email = models.EmailField(unique=True)
    pending_email = models.EmailField(blank=True, null=True)  # noqa: DJ001
    pending_email_code = models.CharField(max_length=6, blank=True, null=True)  # noqa: DJ001
    pending_email_code_expires = models.DateTimeField(blank=True, null=True)
    publish_blocked = models.BooleanField(default=False)
    hourly_post_limit = models.PositiveIntegerField(default=5)
    daily_post_limit = models.PositiveIntegerField(default=30)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def save(self, *args, **kwargs):
        if self.role == "admin":
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)
