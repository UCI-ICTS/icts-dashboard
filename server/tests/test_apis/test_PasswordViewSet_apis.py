# #!/usr/bin/env python3
# tests/test_apps/test_metadata/test_apis/test_PasswordViewSet_apis.py

from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class PasswordViewSetTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_request_reset(self):
        response_200 = self.client.post(
            "/api/auth/password/reset/", {"email": "test@example.com"}
        )
        response_404 = self.client.post(
            "/api/auth/password/reset/", {"email": "bad@example.com"}
        )

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertIn("message", response_200.data)
        self.assertIn("Password reset link sent.", response_200.data["message"])

        # Check the email content
        self.assertEqual(len(mail.outbox), 1)
        reset_email = mail.outbox[0]
        self.assertIn("Reset your password", reset_email.subject)
        self.assertIn("test@example.com", reset_email.to)

        # Extract the reset URL
        reset_url = None
        for line in reset_email.body.splitlines():
            if "http" in line:
                reset_url = line.strip()
                break

        # Confirm a URL was extracted
        self.assertIsNotNone(reset_url, "No reset URL found in the email body.")

        # Confirm bad email fail
        self.assertEqual(response_404.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error", response_404.data)
        self.assertIn("No user found with this email", response_404.data["error"])

    def test_reset_confirm(self):
        # Trigger the email
        self.client.post("/api/auth/password/reset/", {"email": "test@example.com"})

        # Extract token from email
        reset_email = mail.outbox[0]
        reset_url = next(
            line for line in reset_email.body.splitlines() if "http" in line
        )

        # Parse the URL to extract uid and token
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(reset_url)
        query_params = parse_qs(parsed.query)
        uid = query_params["uid"][0]
        token = query_params["token"][0]

        # Submit new password
        response = self.client.post(
            "/api/auth/password/confirm/",
            {"uid": uid, "token": token, "new_password": "NewSecurePass123!"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_password_change(self):
        response = self.client.post(
            "/api/auth/token/login/",
            {"username": "testuser", "password": "testpass123"},
        )
        access_token = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response_200 = self.client.post(
            "/api/auth/password/change/",
            {
                "old_password": "testpass123",
                "new_password": "NewSecurePass123",
                "confirm_new_password": "NewSecurePass123",
            },
        )

        self.assertEqual(response_200.status_code, status.HTTP_200_OK)
        self.assertIn("detail", response_200.data)
        self.assertIn("Password changed successfully", response_200.data["detail"])

        response_400 = self.client.post(
            "/api/auth/password/change/",
            {
                "old_password": "testpass123",
                "new_password": "string",
                "confirm_new_password": "string2",
            },
        )

        self.assertEqual(response_400.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response_400.data)
