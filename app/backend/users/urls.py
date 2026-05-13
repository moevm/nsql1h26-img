from django.urls import path

from .views import (
    ChangePasswordView,
    ConfirmEmailChangeView,
    LoginView,
    LogoutView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    UserPublicView,
    UserPublishSettingsView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path(
        "users/<str:username>/publish-settings/",
        UserPublishSettingsView.as_view(),
        name="user-publish-settings",
    ),
    path("users/<str:username>/", UserPublicView.as_view(), name="user-public"),
    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("password/change/", ChangePasswordView.as_view(), name="password-change"),
    path("email/confirm/", ConfirmEmailChangeView.as_view(), name="email-confirm"),
]
