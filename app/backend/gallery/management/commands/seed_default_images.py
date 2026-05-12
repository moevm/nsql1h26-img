import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image as PillowImage
from PIL import UnidentifiedImageError

from gallery.models import Image
from logs.models import ActionType, Log

User = get_user_model()

DEFAULT_AUTHOR = {
    "username": "user",
    "email": "user@stocker.dev",
    "password": "user1234",
    "role": "user",
}
DEFAULT_IMAGES_DIR = Path(__file__).resolve().parents[2] / "default_images"
MANIFEST_FILENAME = "manifest.json"
SUPPORTED_EXTENSIONS = {".gif", ".jpeg", ".jpg", ".png", ".webp"}


class Command(BaseCommand):
    help = (
        "Load default gallery images from gallery/default_images when gallery is empty"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-dir",
            default=str(DEFAULT_IMAGES_DIR),
            help="Directory with default image files.",
        )

    def handle(self, *args, **options):
        if Image.objects.exists():
            self.stdout.write("Gallery already contains images, skipping seed.")
            return

        source_dir = Path(options["source_dir"]).resolve()
        image_paths = self._get_image_paths(source_dir)
        if not image_paths:
            self.stdout.write(
                self.style.WARNING(
                    f"No default images found in '{source_dir}', skipping seed."
                )
            )
            return

        author = self._get_or_create_default_author()
        manifest = self._load_manifest(source_dir)

        created_count = 0
        for image_path in image_paths:
            if not self._is_valid_image(image_path):
                self.stderr.write(f"Skipping unsupported image file: {image_path.name}")
                continue

            metadata = manifest.get(image_path.name, {})
            image = Image(
                title=metadata.get("title") or self._title_from_filename(image_path),
                description=metadata.get("description", ""),
                author=author,
            )
            image.file.save(
                image_path.name,
                ContentFile(image_path.read_bytes()),
                save=True,
            )

            Log.add_log(
                user=author,
                action=ActionType.IMAGE_UPLOADED,
                payload={
                    "source": "default_seed",
                    "image_id": str(image.id),
                    "title": image.title,
                    "file_path": image.file.name if image.file else "",
                    "image_format": image.image_format,
                    "file_size_mb": image.file_size_mb,
                },
            )
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Created {created_count} default gallery images.")
        )

    def _get_image_paths(self, source_dir: Path) -> list[Path]:
        if not source_dir.exists():
            return []

        return sorted(
            path
            for path in source_dir.iterdir()
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    def _load_manifest(self, source_dir: Path) -> dict:
        manifest_path = source_dir / MANIFEST_FILENAME
        if not manifest_path.exists():
            return {}

        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            self.stderr.write(f"Cannot read default image manifest: {error}")
            return {}

    def _is_valid_image(self, image_path: Path) -> bool:
        try:
            with PillowImage.open(image_path) as image:
                image.verify()
        except OSError, UnidentifiedImageError:
            return False
        return True

    def _get_or_create_default_author(self):
        user = User.objects.filter(username=DEFAULT_AUTHOR["username"]).first()
        if user:
            return user

        user = User.objects.filter(email=DEFAULT_AUTHOR["email"]).first()
        if user:
            return user

        user = User(
            username=DEFAULT_AUTHOR["username"],
            email=DEFAULT_AUTHOR["email"],
            role=DEFAULT_AUTHOR["role"],
        )
        user.set_password(DEFAULT_AUTHOR["password"])
        user.save()
        return user

    def _title_from_filename(self, image_path: Path) -> str:
        return image_path.stem.replace("-", " ").replace("_", " ").title()
