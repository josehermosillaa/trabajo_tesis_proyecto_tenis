from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class AuthenticationAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.username = "testuser"
        self.password = "TestPassword123!"

        User = get_user_model()

        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": self.username,
                "password": "WrongPassword123!",
            },
            format="json"
        )

        self.assertEqual(response.status_code, 401)

    def test_refresh_access_token(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": self.username,
                "password": self.password,
            },
            format="json"
        )

        self.assertEqual(response.status_code, 200)

        refresh_token = response.data["refresh"]

        refresh_response = self.client.post(
            "/api/token/refresh/",
            {
                "refresh": refresh_token,
            },
            format="json"
        )

        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)