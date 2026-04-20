from django.urls import path

from .views import LoginView, LogoutView, MeView, RegisterView, UserPublicView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", LoginView.as_view(), name="auth-login"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", MeView.as_view(), name="auth-me"),
    path("users/<str:username>/", UserPublicView.as_view(), name="user-public"),
]
