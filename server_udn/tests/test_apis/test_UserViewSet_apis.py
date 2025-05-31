# #!/usr/bin/env python3
# tests/test_apps/test_metadata/test_apis/test_UserViewSet_apis.py

from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()


class UserViewSetTests(APITestCase):
    fixtures = ["tests/fixtures/test_fixture.json"]

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.superuser = User.objects.create_user(
            username="admin", password="adminpass", is_superuser=True
        )

    def test_authenticated_list_users(self):
        url = "/api/auth/users/"
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)

    def test_unauthenticated_list_users(self):
        url = "/api/auth/users/"
        self.client.force_authenticate(user=None)  # remove auth
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_authenticated_distroy_users(self):
        url = "/api/auth/users/wheel/"
        self.client.force_authenticate(user=self.superuser)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_insufficeint_perms_distroy_users(self):
        url = "/api/auth/users/testuser/"
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)

    def test_unauthenticated_distroy_users(self):
        url = "/api/auth/users/wheel/"
        self.client.force_authenticate(user=None)  # remove auth
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
