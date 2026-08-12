from django.test import TestCase
from rest_framework.test import APIClient

from authentication.models import Role, User


class AuthenticationAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.role = Role.objects.create(
            name="Administrador"
        )

        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            email="testuser@tenis.cl",
            role=self.role,
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": "testuser",
                "password": "testpassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    def test_refresh_access_token(self):
        login_response = self.client.post(
            "/api/token/",
            {
                "username": "testuser",
                "password": "testpassword",
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)

        refresh_token = login_response.data["refresh"]

        response = self.client.post(
            "/api/token/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)