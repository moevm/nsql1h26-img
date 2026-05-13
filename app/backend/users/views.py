import datetime
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from logs.models import ActionType, Log

from .serializers import (
    AdminPublishSettingsSerializer,
    ChangePasswordSerializer,
    ConfirmEmailChangeSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
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

        Log.add_log(
            user=user,
            action=ActionType.USER_REGISTERED,
            payload={
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
            },
        )

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

        user_agent = request.META.get("HTTP_USER_AGENT", "")
        payload = {"user_agent": user_agent}
        if not getattr(user, "is_staff", False):
            payload["ip_address"] = request.META.get(
                "HTTP_X_REAL_IP"
            ) or request.META.get("REMOTE_ADDR", "")

        Log.add_log(
            user=user,
            action=ActionType.USER_LOGGED_IN,
            payload=payload,
        )

        return Response(
            {"token": token.key, "user": UserMeSerializer(user).data},
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payload = {}
        if not getattr(request.user, "is_staff", False):
            payload["ip_address"] = request.META.get(
                "HTTP_X_REAL_IP"
            ) or request.META.get("REMOTE_ADDR", "")

        Log.add_log(
            user=request.user,
            action=ActionType.USER_LOGGED_OUT,
            payload=payload,
        )

        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        old_values = {
            key: getattr(request.user, key, None)
            for key in serializer.validated_data.keys()
        }

        user = serializer.save()

        changes = {}
        for key, old_val in old_values.items():
            new_val = getattr(user, key, None)
            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val}

        if getattr(serializer, "email_changed", False):
            code = str(secrets.randbelow(900000) + 100000)
            now = datetime.datetime.now(datetime.UTC)
            expires = now + datetime.timedelta(minutes=15)
            user.pending_email_code = code
            user.pending_email_code_expires = expires
            user.save(
                update_fields=[
                    "pending_email_code",
                    "pending_email_code_expires",
                ]
            )
            body = (
                f"To: {user.pending_email}\n"
                f"From: noreply@stocker.dev\n"
                f"Subject: Подтверждение смены email — Stocker\n"
                f"Date: {now.strftime('%a, %d %b %Y %H:%M:%S %z')}\n"
                f"\n"
                f"Ваш код подтверждения для смены email: {code}\n\n"
                f"Код действителен 15 минут. Если вы не запрашивали смену email — "
                f"проигнорируйте это письмо.\n"
            )
            print(body, flush=True)

        payload = {"changes": changes}
        if not getattr(request.user, "is_staff", False):
            payload["ip_address"] = request.META.get(
                "HTTP_X_REAL_IP"
            ) or request.META.get("REMOTE_ADDR", "")

        Log.add_log(
            user=request.user,
            action=ActionType.PROFILE_UPDATED,
            payload=payload,
        )

        return Response(UserMeSerializer(user).data, status=status.HTTP_200_OK)


class UserPublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("User not found.")
        serializer = UserPublicSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserPublishSettingsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("User not found.")
        if user.role == "admin":
            return Response(
                {"detail": "Нельзя изменять настройки публикаций для администраторов."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = AdminPublishSettingsSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        old_values = {
            key: getattr(user, key, None) for key in serializer.validated_data.keys()
        }

        serializer.save()

        changes = {}
        for key, old_val in old_values.items():
            new_val = getattr(user, key, None)
            if old_val != new_val:
                changes[key] = {"old": old_val, "new": new_val}

        Log.add_log(
            user=request.user,
            action=ActionType.ADMIN_USER_RESTRICTIONS_UPDATED,
            payload={
                "target_user_id": str(user.id),
                "target_username": user.username,
                "changes": changes,
            },
        )

        return Response(UserPublicSerializer(user).data, status=status.HTTP_200_OK)


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
            print(body, flush=True)

        return Response(
            {"detail": "Если такой email зарегистрирован, письмо отправлено."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        payload = {"email": user.email}
        if not getattr(user, "is_staff", False):
            payload["ip_address"] = request.META.get(
                "HTTP_X_REAL_IP"
            ) or request.META.get("REMOTE_ADDR", "")

        Log.add_log(
            user=user,
            action=ActionType.PASSWORD_RECOVERED,
            payload=payload,
        )

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

        payload = {"email": request.user.email}
        if not getattr(request.user, "is_staff", False):
            payload["ip_address"] = request.META.get(
                "HTTP_X_REAL_IP"
            ) or request.META.get("REMOTE_ADDR", "")

        Log.add_log(
            user=request.user,
            action=ActionType.PASSWORD_CHANGED,
            payload=payload,
        )

        return Response({"token": new_token.key}, status=status.HTTP_200_OK)


class ConfirmEmailChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConfirmEmailChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        old_email = request.user.email
        user = serializer.save()

        payload = {"old_email": old_email}
        if not getattr(request.user, "is_staff", False):
            payload["ip_address"] = request.META.get(
                "HTTP_X_REAL_IP"
            ) or request.META.get("REMOTE_ADDR", "")

        Log.add_log(
            user=request.user,
            action=ActionType.EMAIL_CHANGED,
            payload=payload,
        )

        return Response(UserMeSerializer(user).data, status=status.HTTP_200_OK)
