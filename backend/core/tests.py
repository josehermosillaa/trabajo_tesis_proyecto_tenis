from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from authentication.models import Role
from core.models import Player,Competition, Category


class HealthAPITest(TestCase):

    def test_health_endpoint(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "OK")


class PlayerAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Crear roles
        self.admin_role = Role.objects.create(
            name="Administrador"
        )

        self.organizer_role = Role.objects.create(
            name="Organizador"
        )

        self.player_role = Role.objects.create(
            name="Jugador"
        )

        User = get_user_model()

        # Usuario administrador
        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="TestPassword123!",
            email="admin@test.cl",
            role=self.admin_role,
        )

        # Usuario organizador
        self.organizer_user = User.objects.create_user(
            username="organizer_test",
            password="TestPassword123!",
            email="organizer@test.cl",
            role=self.organizer_role,
        )

        # Usuario jugador
        self.player_user = User.objects.create_user(
            username="player_test",
            password="TestPassword123!",
            email="player@test.cl",
            role=self.player_role,
        )

    def authenticate(self, user):
        response = self.client.post(
            "/api/token/",
            {
                "username": user.username,
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def test_list_players_authenticated(self):
        self.authenticate(self.admin_user)

        response = self.client.get("/api/players/")

        self.assertEqual(response.status_code, 200)

    def test_create_player(self):
        self.authenticate(self.admin_user)

        data = {
            "user": self.admin_user.id,
            "rut": "22222222-2",
            "first_name": "Juan",
            "last_name": "Pérez",
            "birth_date": "1995-05-20",
            "phone": "+56987654321",
        }

        response = self.client.post(
            "/api/players/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["rut"], "22222222-2")

    def test_get_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            rut="33333333-3",
            first_name="Pedro",
            last_name="González",
            birth_date="1990-10-15",
            phone="+56911111111",
        )

        self.authenticate(self.admin_user)

        response = self.client.get(
            f"/api/players/{player.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], player.id)

    def test_update_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            rut="44444444-4",
            first_name="Carlos",
            last_name="Pérez",
            birth_date="1992-03-10",
            phone="+56922222222",
        )

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/players/{player.id}/",
            {
                "phone": "+56999999999",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["phone"],
            "+56999999999",
        )

    def test_duplicate_rut(self):
        Player.objects.create(
            user=self.admin_user,
            rut="55555555-5",
            first_name="Ana",
            last_name="Soto",
            birth_date="1993-07-12",
            phone="+56933333333",
        )

        User = get_user_model()

        second_user = User.objects.create_user(
            username="secondplayer",
            password="TestPassword123!",
            email="secondplayer@tenis.cl",
            role=self.admin_role,
        )

        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/players/",
            {
                "user": second_user.id,
                "rut": "55555555-5",
                "first_name": "Otra",
                "last_name": "Persona",
                "birth_date": "1994-08-20",
                "phone": "+56944444444",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    # -----------------------------
    # TESTS DE PERMISOS POR ROL
    # -----------------------------

    def test_organizer_can_create_player(self):
        self.authenticate(self.organizer_user)

        data = {
            "user": self.organizer_user.id,
            "rut": "66666666-6",
            "first_name": "Organizador",
            "last_name": "Prueba",
            "birth_date": "1990-01-01",
            "phone": "+56955555555",
        }

        response = self.client.post(
            "/api/players/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_organizer_cannot_delete_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            rut="77777777-7",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56966666666",
        )

        self.authenticate(self.organizer_user)

        response = self.client.delete(
            f"/api/players/{player.id}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_player_can_view_players(self):
        player = Player.objects.create(
            user=self.admin_user,
            rut="88888888-8",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56977777777",
        )

        self.authenticate(self.player_user)

        response = self.client.get(
            f"/api/players/{player.id}/"
        )

        self.assertEqual(response.status_code, 200)

    def test_player_cannot_create_player(self):
        self.authenticate(self.player_user)

        data = {
            "user": self.player_user.id,
            "rut": "99999999-9",
            "first_name": "Nuevo",
            "last_name": "Jugador",
            "birth_date": "1990-01-01",
            "phone": "+56988888888",
        }

        response = self.client.post(
            "/api/players/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_update_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            rut="10101010-1",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56977777777",
        )

        self.authenticate(self.player_user)

        response = self.client.patch(
            f"/api/players/{player.id}/",
            {
                "phone": "+56999999999",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_delete_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            rut="12121212-1",
            first_name="Jugador",
            last_name="Eliminar",
            birth_date="1990-01-01",
            phone="+56911111111",
        )

        self.authenticate(self.admin_user)

        response = self.client.delete(
            f"/api/players/{player.id}/"
        )

        self.assertEqual(response.status_code, 204)
        
class CompetitionAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Crear roles
        self.admin_role = Role.objects.create(
            name="Administrador"
        )

        self.organizer_role = Role.objects.create(
            name="Organizador"
        )

        self.player_role = Role.objects.create(
            name="Jugador"
        )

        User = get_user_model()

        # Crear usuarios
        self.admin_user = User.objects.create_user(
            username="competition_admin",
            password="TestPassword123!",
            email="competition_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="competition_organizer",
            password="TestPassword123!",
            email="competition_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="competition_player",
            password="TestPassword123!",
            email="competition_player@tenis.cl",
            role=self.player_role,
        )

    def authenticate(self, user):
        response = self.client.post(
            "/api/token/",
            {
                "username": user.username,
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def create_competition(self):
        return Competition.objects.create(
            name="Torneo de Prueba",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

    # -----------------------------
    # AUTENTICACIÓN
    # -----------------------------

    def test_unauthenticated_user_cannot_list_competitions(self):
        response = self.client.get("/api/competitions/")

        self.assertEqual(response.status_code, 401)

    # -----------------------------
    # ADMINISTRADOR
    # -----------------------------

    def test_admin_can_list_competitions(self):
        self.authenticate(self.admin_user)

        response = self.client.get("/api/competitions/")

        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_competition(self):
        self.authenticate(self.admin_user)

        data = {
            "name": "Torneo Administrador",
            "type": "ELIMINACION_DIRECTA",
            "start_date": "2026-09-01",
            "end_date": "2026-09-15",
            "status": "PENDIENTE",
            "registration_deadline": "2026-08-28",
        }

        response = self.client.post(
            "/api/competitions/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_admin_can_update_competition(self):
        competition = self.create_competition()

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/competitions/{competition.id}/",
            {
                "name": "Torneo Modificado",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["name"],
            "Torneo Modificado",
        )

    def test_admin_can_delete_competition(self):
        competition = self.create_competition()

        self.authenticate(self.admin_user)

        response = self.client.delete(
            f"/api/competitions/{competition.id}/"
        )

        self.assertEqual(response.status_code, 204)

    # -----------------------------
    # ORGANIZADOR
    # -----------------------------

    def test_organizer_can_list_competitions(self):
        self.authenticate(self.organizer_user)

        response = self.client.get("/api/competitions/")

        self.assertEqual(response.status_code, 200)

    def test_organizer_can_create_competition(self):
        self.authenticate(self.organizer_user)

        data = {
            "name": "Torneo Organizador",
            "type": "ESCALERILLA",
            "start_date": "2026-10-01",
            "end_date": "2026-10-30",
            "status": "PENDIENTE",
            "registration_deadline": "2026-09-28",
        }

        response = self.client.post(
            "/api/competitions/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_organizer_can_update_competition(self):
        competition = self.create_competition()

        self.authenticate(self.organizer_user)

        response = self.client.patch(
            f"/api/competitions/{competition.id}/",
            {
                "name": "Torneo Organizador Modificado",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_organizer_cannot_delete_competition(self):
        competition = self.create_competition()

        self.authenticate(self.organizer_user)

        response = self.client.delete(
            f"/api/competitions/{competition.id}/"
        )

        self.assertEqual(response.status_code, 403)

    # -----------------------------
    # JUGADOR
    # -----------------------------

    def test_player_can_list_competitions(self):
        self.authenticate(self.player_user)

        response = self.client.get("/api/competitions/")

        self.assertEqual(response.status_code, 200)

    def test_player_cannot_create_competition(self):
        self.authenticate(self.player_user)

        data = {
            "name": "Torneo Jugador",
            "type": "ELIMINACION_DIRECTA",
            "start_date": "2026-11-01",
            "end_date": "2026-11-15",
            "status": "PENDIENTE",
            "registration_deadline": "2026-10-28",
        }

        response = self.client.post(
            "/api/competitions/",
            data,
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_update_competition(self):
        competition = self.create_competition()

        self.authenticate(self.player_user)

        response = self.client.patch(
            f"/api/competitions/{competition.id}/",
            {
                "name": "Intento de modificación",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_delete_competition(self):
        competition = self.create_competition()

        self.authenticate(self.player_user)

        response = self.client.delete(
            f"/api/competitions/{competition.id}/"
        )

        self.assertEqual(response.status_code, 403)
        
        
class CategoryAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Roles
        self.admin_role = Role.objects.create(
            name="Administrador"
        )

        self.organizer_role = Role.objects.create(
            name="Organizador"
        )

        self.player_role = Role.objects.create(
            name="Jugador"
        )

        User = get_user_model()

        # Usuarios
        self.admin_user = User.objects.create_user(
            username="category_admin",
            password="TestPassword123!",
            email="category_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="category_organizer",
            password="TestPassword123!",
            email="category_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="category_player",
            password="TestPassword123!",
            email="category_player@tenis.cl",
            role=self.player_role,
        )

    def authenticate(self, user):
        response = self.client.post(
            "/api/token/",
            {
                "username": user.username,
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )

    def create_category(self, name="PRIMERA"):
        return Category.objects.create(
            name=name
        )

    # -----------------------------
    # AUTENTICACIÓN
    # -----------------------------

    def test_unauthenticated_user_cannot_list_categories(self):
        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 401)

    # -----------------------------
    # ADMINISTRADOR
    # -----------------------------

    def test_admin_can_list_categories(self):
        self.authenticate(self.admin_user)

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_category(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/categories/",
            {
                "name": "SEGUNDA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "SEGUNDA")

    def test_admin_can_update_category(self):
        category = self.create_category()

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/categories/{category.id}/",
            {
                "name": "SEGUNDA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "SEGUNDA")

    def test_admin_can_delete_category(self):
        category = self.create_category()

        self.authenticate(self.admin_user)

        response = self.client.delete(
            f"/api/categories/{category.id}/"
        )

        self.assertEqual(response.status_code, 204)

    # -----------------------------
    # ORGANIZADOR
    # -----------------------------

    def test_organizer_can_list_categories(self):
        self.authenticate(self.organizer_user)

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 200)

    def test_organizer_can_create_category(self):
        self.authenticate(self.organizer_user)

        response = self.client.post(
            "/api/categories/",
            {
                "name": "SEGUNDA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_organizer_can_update_category(self):
        category = self.create_category()

        self.authenticate(self.organizer_user)

        response = self.client.patch(
            f"/api/categories/{category.id}/",
            {
                "name": "SEGUNDA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_organizer_cannot_delete_category(self):
        category = self.create_category()

        self.authenticate(self.organizer_user)

        response = self.client.delete(
            f"/api/categories/{category.id}/"
        )

        self.assertEqual(response.status_code, 403)

    # -----------------------------
    # JUGADOR
    # -----------------------------

    def test_player_can_list_categories(self):
        self.authenticate(self.player_user)

        response = self.client.get("/api/categories/")

        self.assertEqual(response.status_code, 200)

    def test_player_cannot_create_category(self):
        self.authenticate(self.player_user)

        response = self.client.post(
            "/api/categories/",
            {
                "name": "SEGUNDA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_update_category(self):
        category = self.create_category()

        self.authenticate(self.player_user)

        response = self.client.patch(
            f"/api/categories/{category.id}/",
            {
                "name": "SEGUNDA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_delete_category(self):
        category = self.create_category()

        self.authenticate(self.player_user)

        response = self.client.delete(
            f"/api/categories/{category.id}/"
        )

        self.assertEqual(response.status_code, 403)

    # -----------------------------
    # VALIDACIÓN UNIQUE
    # -----------------------------

    def test_duplicate_category_name_is_rejected(self):
        self.create_category("PRIMERA")

        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/categories/",
            {
                "name": "PRIMERA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)