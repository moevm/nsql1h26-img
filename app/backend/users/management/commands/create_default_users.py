from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()

DEFAULT_USERS = [
    {
        "username": "user",
        "email": "user@stocker.dev",
        "password": "user1234",
        "role": "user",
    },
    {
        "username": "admin",
        "email": "admin@stocker.dev",
        "password": "admin1234",
        "role": "admin",
    },
]


class Command(BaseCommand):
    help = "Create default users for testing if they do not exist"

    def handle(self, *args, **kwargs):
        for data in DEFAULT_USERS:
            if User.objects.filter(username=data["username"]).exists():
                self.stdout.write(
                    f"User '{data['username']}' already exists, skipping."
                )
                continue
            user = User(
                username=data["username"],
                email=data["email"],
                role=data["role"],
            )
            user.set_password(data["password"])
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created user '{data['username']}' (role: {data['role']})"
                )
            )
