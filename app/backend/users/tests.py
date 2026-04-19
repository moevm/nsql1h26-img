from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()


class AuthAPITestCase(APITestCase):
    def setUp(self):
        self.existing_user = User.objects.create_user(
            username="existing",
            email="existing@test.com",
            password="StrongPass1!",
        )
        self.register_url = reverse("auth-register")
        self.login_url = reverse("auth-login")
        self.logout_url = reverse("auth-logout")
        self.me_url = reverse("auth-me")

    # --- REGISTER ---

    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):
        data = {
            "username": "existing",
            "email": "other@test.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_duplicate_email(self):
        data = {
            "username": "newuser",
            "email": "existing@test.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_password_mismatch(self):
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "StrongPass1!",
            "password2": "WrongPass1!",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "123",
            "password2": "123",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_ignores_role_admin(self):
        data = {
            "username": "newuser",
            "email": "new@test.com",
            "password": "StrongPass1!",
            "password2": "StrongPass1!",
            "role": "admin",
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="newuser")
        self.assertEqual(user.role, "user")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    # --- LOGIN ---

    def test_login_with_username(self):
        data = {"login": "existing", "password": "StrongPass1!"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_with_email(self):
        data = {"login": "existing@test.com", "password": "StrongPass1!"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_invalid_credentials(self):
        data = {"login": "existing", "password": "wrongpass"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_rotates_token(self):
        old_token = Token.objects.create(user=self.existing_user)
        data = {"login": "existing", "password": "StrongPass1!"}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["token"], old_token.key)
        self.assertEqual(Token.objects.filter(user=self.existing_user).count(), 1)

    # --- LOGOUT ---

    def test_logout_unauthenticated(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalidates_token(self):
        token = Token.objects.create(user=self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.existing_user).exists())

    # --- ME ---

    def test_me_unauthenticated(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_data(self):
        token = Token.objects.create(user=self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "existing")
        self.assertEqual(response.data["email"], "existing@test.com")

    def test_me_no_password_exposed(self):
        token = Token.objects.create(user=self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.get(self.me_url)
        self.assertNotIn("password", response.data)
