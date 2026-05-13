import os
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.http import FileResponse
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from logs.models import ActionType, Log

BACKUP_APPS = ["users", "gallery", "logs", "authtoken"]
MAX_UNCOMPRESSED_SIZE = 5 * 1024 * 1024 * 1024


class AutoDeleteFileResponse(FileResponse):
    def __init__(self, file_path, *args, **kwargs):
        super().__init__(open(file_path, "rb"), *args, **kwargs)
        self.file_path = Path(file_path)

    def close(self):
        super().close()
        try:
            if self.file_path.exists():
                self.file_path.unlink()
        except Exception:
            pass


class SystemExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request: Request) -> FileResponse:
        temp_dir = tempfile.mkdtemp()
        base_temp_path = Path(temp_dir)

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"stocker_backup_{timestamp}.zip"

            Log.add_log(
                user=request.user,
                action=ActionType.DATABASE_EXPORTED,
                payload={
                    "format": "json",
                    "archive_name": archive_name,
                },
            )

            db_json_path = base_temp_path / "db.json"
            with open(db_json_path, "w", encoding="utf-8") as db_file:
                call_command(
                    "dumpdata",
                    *BACKUP_APPS,
                    format="json",
                    stdout=db_file,
                )

            uploads_source = Path(settings.MEDIA_ROOT) / "uploads"
            uploads_dest = base_temp_path / "uploads"
            if uploads_source.exists():
                shutil.copytree(uploads_source, uploads_dest)
            else:
                uploads_dest.mkdir(parents=True, exist_ok=True)

            archive_path = Path(tempfile.gettempdir()) / archive_name

            with zipfile.ZipFile(
                archive_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6
            ) as zf:
                for root, _, files in os.walk(base_temp_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(base_temp_path)
                        zf.write(file_path, arcname)

            return AutoDeleteFileResponse(
                archive_path,
                as_attachment=True,
                filename=archive_name,
            )

        finally:
            shutil.rmtree(base_temp_path, ignore_errors=True)


class SystemImportView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser]

    def post(self, request: Request) -> Response:
        archive_file = request.FILES.get("archive")
        if not archive_file or not archive_file.name.endswith(".zip"):
            return Response(
                {"detail": "Необходимо загрузить корректный .zip архив."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        temp_dir = tempfile.mkdtemp()
        extract_path = Path(temp_dir)
        uploads_target = Path(settings.MEDIA_ROOT) / "uploads"
        uploads_backup = Path(settings.MEDIA_ROOT) / "uploads_rollback_backup"

        try:
            temp_archive_path = extract_path / "uploaded_source_archive.zip"
            with open(temp_archive_path, "wb") as f:
                for chunk in archive_file.chunks():
                    f.write(chunk)

            uncompressed_size = 0
            with zipfile.ZipFile(temp_archive_path, "r") as zf:
                for info in zf.infolist():
                    if (
                        ".." in info.filename
                        or info.filename.startswith("/")
                        or info.filename.startswith("\\")
                    ):
                        return Response(
                            {"detail": "Архив содержит небезопасные пути."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    uncompressed_size += info.file_size
                    if uncompressed_size > MAX_UNCOMPRESSED_SIZE:
                        return Response(
                            {"detail": ("Превышен лимит размера распаковки ")},
                            status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        )

                zf.extractall(extract_path)

            db_json_path = extract_path / "db.json"
            if not db_json_path.exists():
                return Response(
                    {"detail": "В архиве отсутствует файл db.json."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            records_inserted = 0
            with open(db_json_path, encoding="utf-8") as f:
                for line in f:
                    records_inserted += line.count('"model":')

            if records_inserted == 0:
                return Response(
                    {"detail": "Файл db.json пуст или поврежден."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if uploads_backup.exists():
                shutil.rmtree(uploads_backup, ignore_errors=True)
            if uploads_target.exists():
                uploads_target.rename(uploads_backup)
            uploads_target.mkdir(parents=True, exist_ok=True)

            rollback_db_path = extract_path / "rollback_db.json"
            try:
                with open(rollback_db_path, "w", encoding="utf-8") as f:
                    call_command("dumpdata", *BACKUP_APPS, format="json", stdout=f)
            except Exception:
                pass

            try:
                call_command("flush", interactive=False)

                uploads_arc = extract_path / "uploads"
                if uploads_arc.exists():
                    shutil.copytree(uploads_arc, uploads_target, dirs_exist_ok=True)

                call_command("loaddata", str(db_json_path))

            except Exception as critical_error:
                shutil.rmtree(uploads_target, ignore_errors=True)
                if uploads_backup.exists():
                    uploads_backup.rename(uploads_target)

                if rollback_db_path.exists():
                    try:
                        call_command("loaddata", str(rollback_db_path))
                    except Exception:
                        pass

                return Response(
                    {
                        "detail": (
                            "Сбой импорта БД. Выполнен откат БД и медиафайлов. "
                            f"Причина: {str(critical_error)}"
                        )
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            shutil.rmtree(uploads_backup, ignore_errors=True)

            User = get_user_model()
            current_user = User.objects.filter(pk=request.user.pk).first()

            Log.add_log(
                user=current_user,
                action=ActionType.DATABASE_IMPORTED,
                payload={
                    "source_file": archive_file.name,
                    "records_inserted": records_inserted,
                    "collections_affected": BACKUP_APPS,
                },
            )

            return Response(
                {
                    "detail": "Система успешно восстановлена.",
                    "records_inserted": records_inserted,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:
            shutil.rmtree(uploads_backup, ignore_errors=True)
            return Response(
                {"detail": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        finally:
            shutil.rmtree(extract_path, ignore_errors=True)
