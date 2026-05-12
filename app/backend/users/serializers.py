from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        validated_data["role"] = "user"
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        login = attrs.get("login")
        password = attrs.get("password")

        user = None
        if "@" in login:
            try:
                candidate = User.objects.get(email=login)
                if candidate.check_password(password):
                    user = candidate
            except User.DoesNotExist:
                pass
        else:
            user = authenticate(
                request=self.context.get("request"),
                username=login,
                password=password,
            )

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials.", code="authorization"
            )
        if not user.is_active:
            raise serializers.ValidationError(
                "Account is disabled.", code="authorization"
            )

        attrs["user"] = user
        return attrs


class UserMeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role", "date_joined"]
        read_only_fields = ["id", "username", "email", "role", "date_joined"]


class UserPublicSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "date_joined"]
        read_only_fields = fields


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True)

    def validate_email(self, value):
        try:
            self.context["reset_user"] = User.objects.get(email=value)
        except User.DoesNotExist:
            self.context["reset_user"] = None
        return value

    def get_user(self):
        return self.context.get("reset_user")

    def get_uid_and_token(self):
        user = self.get_user()
        if user is None:
            return None, None
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
        token = PasswordResetTokenGenerator().make_token(user)
        return uid, token


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(write_only=True)
    token = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            pk = force_str(urlsafe_base64_decode(attrs["uid"]))
            user = User.objects.get(pk=pk)
        except TypeError, ValueError, User.DoesNotExist:
            raise serializers.ValidationError({"uid": "Недействительная ссылка."})

        if not PasswordResetTokenGenerator().check_token(user, attrs["token"]):
            raise serializers.ValidationError(
                {"token": "Ссылка недействительна или срок её действия истёк."}
            )

        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают."})

        validate_password(attrs["new_password"], user)
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = self.context["request"].user

        if not user.check_password(attrs["old_password"]):
            raise serializers.ValidationError(
                {"old_password": "Неверный текущий пароль."}
            )

        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают."})

        validate_password(attrs["new_password"], user)
        attrs["user"] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
