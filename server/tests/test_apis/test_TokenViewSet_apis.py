# #!/usr/bin/env python3
# tests/test_apps/test_metadata/test_apis/test_TokenViewSet_apis.py

from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TokenViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/auth/token/login/",
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_failure(self):
        response = self.client.post(
            "/api/auth/token/login/", {"username": "testuser", "password": "wrongpass"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)
        response = self.client.post(
            "/api/auth/token/refresh/", {"refresh": str(refresh)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_verify_token(self):
        access = RefreshToken.for_user(self.user).access_token
        response = self.client.post("/api/auth/token/verify/", {"token": str(access)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Token is valid.")

    def test_logout_token_blacklist(self):
        refresh_token = RefreshToken.for_user(self.user)
        access_token = str(refresh_token.access_token)

        # Auth header required because logout requires authentication
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.post(
            "/api/auth/token/logout/", {"refresh": str(refresh_token)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Token successfully blacklisted.")

    def test_logout_missing_token(self):
        response = self.client.post("/api/auth/token/logout/", {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
