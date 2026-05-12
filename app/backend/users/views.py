import datetime
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UserMeSerializer,
    UserPublicSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user": UserMeSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        Token.objects.filter(user=user).delete()
        token = Token.objects.create(user=user)
        return Response(
            {"token": token.key, "user": UserMeSerializer(user).data},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("User not found.")
        serializer = UserPublicSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        uid, token = serializer.get_uid_and_token()
        if uid is not None:
            reset_url = (
                f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            )
            recipient = serializer.validated_data["email"]
            now = datetime.datetime.now(datetime.UTC)
            body = (
                f"To: {recipient}\n"
                f"From: noreply@stocker.dev\n"
                f"Subject: Восстановление пароля — Stocker\n"
                f"Date: {now.strftime('%a, %d %b %Y %H:%M:%S %z')}\n"
                f"\n"
                f"Для сброса пароля перейдите по ссылке:\n\n"
                f"{reset_url}\n\n"
                f"Ссылка действительна 3 дня. Если вы не запрашивали сброс — "
                f"проигнорируйте это письмо.\n"
            )
            email_dir = Path(settings.EMAIL_FILE_PATH)
            email_dir.mkdir(parents=True, exist_ok=True)
            filename = email_dir / f"{now.strftime('%Y%m%d-%H%M%S-%f')}.txt"
            filename.write_text(body, encoding="utf-8")

        return Response(
            {"detail": "Если такой email зарегистрирован, письмо отправлено."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        Token.objects.filter(user=request.user).delete()
        new_token = Token.objects.create(user=request.user)

        return Response({"token": new_token.key}, status=status.HTTP_200_OK)
