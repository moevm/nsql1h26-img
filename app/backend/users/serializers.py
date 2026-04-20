from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
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
