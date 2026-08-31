from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import Role, User


class OrganizerManagementAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role = Role.objects.create(name="Administrador")
        self.organizer_role = Role.objects.create(name="Organizador")
        self.player_role = Role.objects.create(name="Jugador")
        self.admin = User.objects.create_user(
            username="admin-organizers",
            password="AdminPassword-2026",
            role=self.admin_role,
        )
        self.organizer = User.objects.create_user(
            username="existing-organizer",
            password="OrganizerPassword-2026",
            first_name="Organizador",
            last_name="Existente",
            email="existing.organizer@example.com",
            role=self.organizer_role,
        )
        self.player = User.objects.create_user(
            username="ordinary-player",
            password="PlayerPassword-2026",
            role=self.player_role,
        )
        self.list_url = "/api/organizers/"

    def create_payload(self, **overrides):
        payload = {
            "username": "new-organizer",
            "first_name": "Nuevo",
            "last_name": "Organizador",
            "email": "new.organizer@example.com",
            "password": "SecureOrganizer-2026",
            "password_confirmation": "SecureOrganizer-2026",
        }
        payload.update(overrides)
        return payload

    def test_admin_lists_only_organizers(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.data], [self.organizer.id])
        self.assertNotIn("password", response.data[0])
        self.assertEqual(response.data[0]["role"], "Organizador")

    def test_admin_creates_hashed_organizer_and_cannot_force_admin_role(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            self.create_payload(role="Administrador", is_staff=True, is_superuser=True),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        created = User.objects.get(username="new-organizer")
        self.assertEqual(created.role, self.organizer_role)
        self.assertTrue(created.check_password("SecureOrganizer-2026"))
        self.assertNotEqual(created.password, "SecureOrganizer-2026")
        self.assertFalse(created.is_staff)
        self.assertFalse(created.is_superuser)

    def test_admin_edits_only_basic_fields(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch(
            f"{self.list_url}{self.organizer.id}/",
            {
                "first_name": "Nombre editado",
                "last_name": "Apellido editado",
                "email": "edited.organizer@example.com",
                "role": "Administrador",
                "is_active": False,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.organizer.refresh_from_db()
        self.assertEqual(self.organizer.first_name, "Nombre editado")
        self.assertEqual(self.organizer.email, "edited.organizer@example.com")
        self.assertEqual(self.organizer.role, self.organizer_role)
        self.assertTrue(self.organizer.is_active)

    def test_admin_deactivates_and_reactivates_organizer(self):
        self.client.force_authenticate(self.admin)
        url = f"{self.list_url}{self.organizer.id}/set-active/"
        disabled = self.client.post(url, {"active": False}, format="json")
        self.assertEqual(disabled.status_code, status.HTTP_200_OK)
        self.organizer.refresh_from_db()
        self.assertFalse(self.organizer.is_active)

        self.client.force_authenticate(None)
        login = self.client.post(
            "/api/token/",
            {"username": self.organizer.username, "password": "OrganizerPassword-2026"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(self.admin)
        enabled = self.client.post(url, {"active": True}, format="json")
        self.assertEqual(enabled.status_code, status.HTTP_200_OK)
        self.organizer.refresh_from_db()
        self.assertTrue(self.organizer.is_active)

        self.client.force_authenticate(None)
        login = self.client.post(
            "/api/token/",
            {"username": self.organizer.username, "password": "OrganizerPassword-2026"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)

    def test_organizer_and_player_receive_forbidden_for_management(self):
        for user in (self.organizer, self.player):
            with self.subTest(role=user.role.name):
                self.client.force_authenticate(user)
                detail_url = f"{self.list_url}{self.organizer.id}/"
                active_url = f"{detail_url}set-active/"
                self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(
                    self.client.post(self.list_url, self.create_payload(), format="json").status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(
                    self.client.patch(detail_url, {"first_name": "Ataque"}, format="json").status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(
                    self.client.post(active_url, {"active": False}, format="json").status_code,
                    status.HTTP_403_FORBIDDEN,
                )

    def test_admin_cannot_access_admin_or_player_through_organizer_endpoint(self):
        self.client.force_authenticate(self.admin)
        for user in (self.admin, self.player):
            with self.subTest(role=user.role.name):
                url = f"{self.list_url}{user.id}/"
                self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
                self.assertEqual(
                    self.client.patch(url, {"first_name": "No permitido"}, format="json").status_code,
                    status.HTTP_404_NOT_FOUND,
                )

    def test_create_validates_duplicate_username_email_and_required_fields(self):
        self.client.force_authenticate(self.admin)
        duplicate = self.client.post(
            self.list_url,
            self.create_payload(username=self.organizer.username),
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", duplicate.data)

        invalid_email = self.client.post(
            self.list_url,
            self.create_payload(username="invalid-email", email="not-an-email"),
            format="json",
        )
        self.assertEqual(invalid_email.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", invalid_email.data)

        required = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(required.status_code, status.HTTP_400_BAD_REQUEST)
        for field in (
            "username", "first_name", "last_name", "email",
            "password", "password_confirmation",
        ):
            self.assertIn(field, required.data)

    def test_create_rejects_password_confirmation_mismatch(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            self.list_url,
            self.create_payload(password_confirmation="DifferentPassword-2026"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirmation", response.data)
