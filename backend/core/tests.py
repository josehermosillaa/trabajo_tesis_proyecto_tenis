from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from authentication.models import Role
from core.models import (
    Player,
    Competition, 
    Category, 
    CompetitionCategory,
    Registration,
    Court,
    Match,
    MatchSet,
    Standing
    )


class HealthAPITest(TestCase):

    def test_health_endpoint(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "OK")


class PlayerAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------
        # ROLES
        # -----------------------------

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

        # -----------------------------
        # USUARIOS
        # -----------------------------

        self.admin_user = User.objects.create_user(
            username="admin_test",
            password="TestPassword123!",
            email="admin@test.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="organizer_test",
            password="TestPassword123!",
            email="organizer@test.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="player_test",
            password="TestPassword123!",
            email="player@test.cl",
            role=self.player_role,
        )

        # -----------------------------
        # CATEGORÍA
        # -----------------------------

        self.category = Category.objects.create(
            name="PRIMERA"
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

    # -----------------------------
    # TESTS CRUD
    # -----------------------------

    def test_list_players_authenticated(self):
        self.authenticate(self.admin_user)

        response = self.client.get(
            "/api/players/"
        )

        self.assertEqual(response.status_code, 200)

    def test_create_player(self):
        self.authenticate(self.admin_user)

        data = {
            "user": self.admin_user.id,
            "category": self.category.id,
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

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["rut"],
            "22222222-2"
        )

    def test_get_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            category=self.category,
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

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["id"],
            player.id
        )

    def test_update_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            category=self.category,
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

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["phone"],
            "+56999999999"
        )

    def test_duplicate_rut(self):
        Player.objects.create(
            user=self.admin_user,
            category=self.category,
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
                "category": self.category.id,
                "rut": "55555555-5",
                "first_name": "Otra",
                "last_name": "Persona",
                "birth_date": "1994-08-20",
                "phone": "+56944444444",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # -----------------------------
    # TESTS DE PERMISOS POR ROL
    # -----------------------------

    def test_organizer_can_create_player(self):
        self.authenticate(
            self.organizer_user
        )

        data = {
            "user": self.organizer_user.id,
            "category": self.category.id,
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

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_cannot_delete_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            category=self.category,
            rut="77777777-7",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56966666666",
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.delete(
            f"/api/players/{player.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_can_view_players(self):
        player = Player.objects.create(
            user=self.admin_user,
            category=self.category,
            rut="88888888-8",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56977777777",
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.get(
            f"/api/players/{player.id}/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_player_cannot_create_player(self):
        self.authenticate(
            self.player_user
        )

        data = {
            "user": self.player_user.id,
            "category": self.category.id,
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

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_update_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            category=self.category,
            rut="10101010-1",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56977777777",
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.patch(
            f"/api/players/{player.id}/",
            {
                "phone": "+56999999999",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_admin_can_delete_player(self):
        player = Player.objects.create(
            user=self.admin_user,
            category=self.category,
            rut="12121212-1",
            first_name="Jugador",
            last_name="Eliminar",
            birth_date="1990-01-01",
            phone="+56911111111",
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            f"/api/players/{player.id}/"
        )

        self.assertEqual(
            response.status_code,
            204
        )
        
        
        
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
        
class CompetitionCategoryAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------
        # ROLES
        # -----------------------------

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

        # -----------------------------
        # USUARIOS
        # -----------------------------

        self.admin_user = User.objects.create_user(
            username="cc_admin",
            password="TestPassword123!",
            email="cc_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="cc_organizer",
            password="TestPassword123!",
            email="cc_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="cc_player",
            password="TestPassword123!",
            email="cc_player@tenis.cl",
            role=self.player_role,
        )

        # -----------------------------
        # COMPETENCIA
        # -----------------------------

        self.competition = Competition.objects.create(
            name="Torneo Test",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

        # -----------------------------
        # CATEGORÍA
        # -----------------------------

        self.category = Category.objects.create(
            name="PRIMERA"
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

    def create_competition_category(self):
        return CompetitionCategory.objects.create(
            competition=self.competition,
            category=self.category,
            max_players=16,
            minimum_players=4,
        )

    # -----------------------------
    # AUTENTICACIÓN
    # -----------------------------

    def test_unauthenticated_user_cannot_list_competition_categories(self):
        response = self.client.get(
            "/api/competition-categories/"
        )

        self.assertEqual(response.status_code, 401)

    # -----------------------------
    # ADMINISTRADOR
    # -----------------------------

    def test_admin_can_list_competition_categories(self):
        self.authenticate(self.admin_user)

        response = self.client.get(
            "/api/competition-categories/"
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_competition_category(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/competition-categories/",
            {
                "competition": self.competition.id,
                "category": self.category.id,
                "max_players": 16,
                "minimum_players": 4,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["max_players"],
            16,
        )
        self.assertEqual(
            response.data["minimum_players"],
            4,
        )

    def test_admin_can_update_competition_category(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/competition-categories/"
            f"{competition_category.id}/",
            {
                "max_players": 32,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["max_players"],
            32,
        )

    def test_admin_can_delete_competition_category(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.admin_user)

        response = self.client.delete(
            f"/api/competition-categories/"
            f"{competition_category.id}/"
        )

        self.assertEqual(response.status_code, 204)

    # -----------------------------
    # ORGANIZADOR
    # -----------------------------

    def test_organizer_can_create_competition_category(self):
        self.authenticate(self.organizer_user)

        response = self.client.post(
            "/api/competition-categories/",
            {
                "competition": self.competition.id,
                "category": self.category.id,
                "max_players": 16,
                "minimum_players": 4,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_organizer_can_update_competition_category(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.organizer_user)

        response = self.client.patch(
            f"/api/competition-categories/"
            f"{competition_category.id}/",
            {
                "minimum_players": 8,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["minimum_players"],
            8,
        )

    def test_organizer_cannot_delete_competition_category(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.organizer_user)

        response = self.client.delete(
            f"/api/competition-categories/"
            f"{competition_category.id}/"
        )

        self.assertEqual(response.status_code, 403)

    # -----------------------------
    # JUGADOR
    # -----------------------------

    def test_player_can_list_competition_categories(self):
        self.authenticate(self.player_user)

        response = self.client.get(
            "/api/competition-categories/"
        )

        self.assertEqual(response.status_code, 200)

    def test_player_cannot_create_competition_category(self):
        self.authenticate(self.player_user)

        response = self.client.post(
            "/api/competition-categories/",
            {
                "competition": self.competition.id,
                "category": self.category.id,
                "max_players": 16,
                "minimum_players": 4,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_update_competition_category(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.player_user)

        response = self.client.patch(
            f"/api/competition-categories/"
            f"{competition_category.id}/",
            {
                "max_players": 32,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_delete_competition_category(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.player_user)

        response = self.client.delete(
            f"/api/competition-categories/"
            f"{competition_category.id}/"
        )

        self.assertEqual(response.status_code, 403)

    # -----------------------------
    # VALIDACIÓN
    # -----------------------------

    def test_minimum_players_cannot_exceed_maximum(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/competition-categories/",
            {
                "competition": self.competition.id,
                "category": self.category.id,
                "max_players": 8,
                "minimum_players": 16,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_duplicate_competition_category_is_rejected(self):
        self.create_competition_category()

        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/competition-categories/",
            {
                "competition": self.competition.id,
                "category": self.category.id,
                "max_players": 16,
                "minimum_players": 4,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        
class RegistrationAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------
        # ROLES
        # -----------------------------

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

        # -----------------------------
        # USUARIOS
        # -----------------------------

        self.admin_user = User.objects.create_user(
            username="reg_admin",
            password="TestPassword123!",
            email="reg_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="reg_organizer",
            password="TestPassword123!",
            email="reg_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="reg_player",
            password="TestPassword123!",
            email="reg_player@tenis.cl",
            role=self.player_role,
        )

        # -----------------------------
        # CATEGORÍAS
        # -----------------------------

        self.primera = Category.objects.create(
            name="PRIMERA"
        )

        self.segunda = Category.objects.create(
            name="SEGUNDA"
        )

        # -----------------------------
        # PLAYER
        # -----------------------------

        self.player = Player.objects.create(
            user=self.player_user,
            category=self.primera,
            rut="55555555-5",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56955555555",
        )

        # -----------------------------
        # COMPETITION
        # -----------------------------

        self.competition = Competition.objects.create(
            name="Torneo Registration Test",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

        # -----------------------------
        # COMPETITION CATEGORIES
        # -----------------------------

        self.competition_primera = (
            CompetitionCategory.objects.create(
                competition=self.competition,
                category=self.primera,
                max_players=16,
                minimum_players=4,
            )
        )

        self.competition_segunda = (
            CompetitionCategory.objects.create(
                competition=self.competition,
                category=self.segunda,
                max_players=16,
                minimum_players=4,
            )
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
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

    def create_registration(self):
        return Registration.objects.create(
            competition_category=self.competition_primera,
            player=self.player,
        )

    # -----------------------------
    # AUTENTICACIÓN
    # -----------------------------

    def test_unauthenticated_user_cannot_list_registrations(self):
        response = self.client.get(
            "/api/registrations/"
        )

        self.assertEqual(response.status_code, 401)

    # -----------------------------
    # ADMINISTRADOR
    # -----------------------------

    def test_admin_can_list_registrations(self):
        self.authenticate(self.admin_user)

        response = self.client.get(
            "/api/registrations/"
        )

        self.assertEqual(response.status_code, 200)

    def test_admin_can_create_registration(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": self.player.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data["status"],
            "PENDIENTE",
        )
        self.assertIsNone(
            response.data["seed"]
        )

    def test_admin_can_update_registration(self):
        registration = self.create_registration()

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/registrations/{registration.id}/",
            {
                "status": "CONFIRMADA",
                "seed": 1,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["status"],
            "CONFIRMADA",
        )
        self.assertEqual(
            response.data["seed"],
            1,
        )

    def test_admin_can_delete_registration(self):
        registration = self.create_registration()

        self.authenticate(self.admin_user)

        response = self.client.delete(
            f"/api/registrations/{registration.id}/"
        )

        self.assertEqual(response.status_code, 204)

    # -----------------------------
    # ORGANIZADOR
    # -----------------------------

    def test_organizer_can_create_registration(self):
        self.authenticate(self.organizer_user)

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": self.player.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

    def test_organizer_can_update_registration(self):
        registration = self.create_registration()

        self.authenticate(self.organizer_user)

        response = self.client.patch(
            f"/api/registrations/{registration.id}/",
            {
                "status": "CONFIRMADA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_organizer_cannot_delete_registration(self):
        registration = self.create_registration()

        self.authenticate(self.organizer_user)

        response = self.client.delete(
            f"/api/registrations/{registration.id}/"
        )

        self.assertEqual(response.status_code, 403)

    # -----------------------------
    # JUGADOR
    # -----------------------------

    def test_player_can_list_registrations(self):
        self.authenticate(self.player_user)

        response = self.client.get(
            "/api/registrations/"
        )

        self.assertEqual(response.status_code, 200)

    def test_player_cannot_create_registration(self):
        self.authenticate(self.player_user)

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": self.player.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_update_registration(self):
        registration = self.create_registration()

        self.authenticate(self.player_user)

        response = self.client.patch(
            f"/api/registrations/{registration.id}/",
            {
                "status": "CONFIRMADA",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_player_cannot_delete_registration(self):
        registration = self.create_registration()

        self.authenticate(self.player_user)

        response = self.client.delete(
            f"/api/registrations/{registration.id}/"
        )

        self.assertEqual(response.status_code, 403)

    # -----------------------------
    # REGLA DE NEGOCIO
    # -----------------------------

    def test_player_cannot_register_in_different_category(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_segunda.id
                ),
                "player": self.player.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    # -----------------------------
    # DUPLICADOS
    # -----------------------------

    def test_duplicate_registration_is_rejected(self):
        self.create_registration()

        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": self.player.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    # -----------------------------
    # FECHA AUTOMÁTICA
    # -----------------------------

    def test_registration_date_is_generated_automatically(self):
        self.authenticate(self.admin_user)

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": self.player.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(
            response.data["registration_date"]
        )
        
class CourtAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------
        # ROLES
        # -----------------------------

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

        # -----------------------------
        # USUARIOS
        # -----------------------------

        self.admin_user = User.objects.create_user(
            username="court_admin",
            password="TestPassword123!",
            email="court_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="court_organizer",
            password="TestPassword123!",
            email="court_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="court_player",
            password="TestPassword123!",
            email="court_player@tenis.cl",
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

        self.assertEqual(
            response.status_code,
            200
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

    # -----------------------------
    # AUTENTICACIÓN
    # -----------------------------

    def test_unauthenticated_user_cannot_list_courts(self):
        response = self.client.get(
            "/api/courts/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # -----------------------------
    # ADMINISTRADOR
    # -----------------------------

    def test_admin_can_list_courts(self):
        Court.objects.create(
            name="Cancha 1"
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.get(
            "/api/courts/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_admin_can_create_court(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/courts/",
            {
                "name": "Cancha 1",
                "status": "AVAILABLE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["name"],
            "Cancha 1"
        )

        self.assertEqual(
            response.data["status"],
            "AVAILABLE"
        )

    def test_admin_can_update_court(self):
        court = Court.objects.create(
            name="Cancha 1"
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/courts/{court.id}/",
            {
                "status": "MAINTENANCE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["status"],
            "MAINTENANCE"
        )

    def test_admin_can_delete_court(self):
        court = Court.objects.create(
            name="Cancha 1"
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            f"/api/courts/{court.id}/"
        )

        self.assertEqual(
            response.status_code,
            204
        )

    # -----------------------------
    # ORGANIZADOR
    # -----------------------------

    def test_organizer_can_create_court(self):
        self.authenticate(
            self.organizer_user
        )

        response = self.client.post(
            "/api/courts/",
            {
                "name": "Cancha 2",
                "status": "AVAILABLE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_can_update_court(self):
        court = Court.objects.create(
            name="Cancha 2"
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.patch(
            f"/api/courts/{court.id}/",
            {
                "status": "OCCUPIED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_organizer_cannot_delete_court(self):
        court = Court.objects.create(
            name="Cancha 3"
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.delete(
            f"/api/courts/{court.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # -----------------------------
    # JUGADOR
    # -----------------------------

    def test_player_can_list_courts(self):
        self.authenticate(
            self.player_user
        )

        response = self.client.get(
            "/api/courts/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_player_cannot_create_court(self):
        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/courts/",
            {
                "name": "Cancha 4",
                "status": "AVAILABLE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_update_court(self):
        court = Court.objects.create(
            name="Cancha 4"
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.patch(
            f"/api/courts/{court.id}/",
            {
                "status": "OCCUPIED",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_delete_court(self):
        court = Court.objects.create(
            name="Cancha 5"
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.delete(
            f"/api/courts/{court.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # -----------------------------
    # VALIDACIONES
    # -----------------------------

    def test_duplicate_court_name_is_rejected(self):
        Court.objects.create(
            name="Cancha 6"
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/courts/",
            {
                "name": "Cancha 6",
                "status": "AVAILABLE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_invalid_status_is_rejected(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/courts/",
            {
                "name": "Cancha 7",
                "status": "INVALIDO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_default_status_is_available(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/courts/",
            {
                "name": "Cancha 8",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["status"],
            "AVAILABLE"
        )
        
class MatchAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------
        # ROLES
        # -----------------------------

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

        # -----------------------------
        # USUARIOS
        # -----------------------------

        self.admin_user = User.objects.create_user(
            username="match_admin",
            password="TestPassword123!",
            email="match_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="match_organizer",
            password="TestPassword123!",
            email="match_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="match_player",
            password="TestPassword123!",
            email="match_player@tenis.cl",
            role=self.player_role,
        )

        # -----------------------------
        # CATEGORÍAS
        # -----------------------------

        self.primera = Category.objects.create(
            name="PRIMERA"
        )

        self.segunda = Category.objects.create(
            name="SEGUNDA"
        )

        # -----------------------------
        # PLAYERS
        # -----------------------------

        self.player1_user = User.objects.create_user(
            username="match_player1",
            password="TestPassword123!",
            email="match_player1@tenis.cl",
            role=self.player_role,
        )

        self.player2_user = User.objects.create_user(
            username="match_player2",
            password="TestPassword123!",
            email="match_player2@tenis.cl",
            role=self.player_role,
        )

        self.player3_user = User.objects.create_user(
            username="match_player3",
            password="TestPassword123!",
            email="match_player3@tenis.cl",
            role=self.player_role,
        )

        self.player1 = Player.objects.create(
            user=self.player1_user,
            category=self.primera,
            rut="11111111-1",
            first_name="Jugador",
            last_name="Uno",
        )

        self.player2 = Player.objects.create(
            user=self.player2_user,
            category=self.primera,
            rut="22222222-2",
            first_name="Jugador",
            last_name="Dos",
        )

        self.player3 = Player.objects.create(
            user=self.player3_user,
            category=self.segunda,
            rut="33333333-3",
            first_name="Jugador",
            last_name="Tres",
        )

        # -----------------------------
        # COMPETENCIAS
        # -----------------------------

        self.competition_elimination = Competition.objects.create(
            name="Torneo Match Eliminación",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

        self.competition_ladder = Competition.objects.create(
            name="Torneo Match Escalerilla",
            type="ESCALERILLA",
            start_date="2026-10-01",
            end_date="2026-10-15",
            registration_deadline="2026-09-28",
        )

        # -----------------------------
        # COMPETITION CATEGORIES
        # -----------------------------

        self.elimination_category = (
            CompetitionCategory.objects.create(
                competition=self.competition_elimination,
                category=self.primera,
                max_players=16,
                minimum_players=4,
            )
        )

        self.ladder_category = (
            CompetitionCategory.objects.create(
                competition=self.competition_ladder,
                category=self.primera,
                max_players=16,
                minimum_players=2,
            )
        )

        # -----------------------------
        # COURT
        # -----------------------------

        self.court = Court.objects.create(
            name="Cancha Match 1"
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

        self.assertEqual(
            response.status_code,
            200
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

    def create_match(self):
        return Match.objects.create(
            competition_category=self.elimination_category,
            court=self.court,
            player1=self.player1,
            player2=self.player2,
            round=1,
        )

    # -----------------------------
    # AUTENTICACIÓN
    # -----------------------------

    def test_unauthenticated_user_cannot_list_matches(self):
        response = self.client.get(
            "/api/matches/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # -----------------------------
    # ADMINISTRADOR
    # -----------------------------

    def test_admin_can_list_matches(self):
        self.create_match()

        self.authenticate(
            self.admin_user
        )

        response = self.client.get(
            "/api/matches/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_admin_can_create_match(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "court": self.court.id,
                "player1": self.player1.id,
                "player2": self.player2.id,
                "round": 1,
                "is_walkover": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["status"],
            "PROGRAMADO"
        )

        self.assertFalse(
            response.data["is_walkover"]
        )

    def test_admin_can_update_match(self):
        match = self.create_match()

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {
                "status": "FINALIZADO",
                "winner_player": self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["status"],
            "FINALIZADO"
        )

        self.assertEqual(
            response.data["winner_player"],
            self.player1.id
        )

    def test_admin_can_delete_match(self):
        match = self.create_match()

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            f"/api/matches/{match.id}/"
        )

        self.assertEqual(
            response.status_code,
            204
        )

    # -----------------------------
    # ORGANIZADOR
    # -----------------------------

    def test_organizer_can_create_match(self):
        self.authenticate(
            self.organizer_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "court": self.court.id,
                "player1": self.player1.id,
                "player2": self.player2.id,
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_can_update_match(self):
        match = self.create_match()

        self.authenticate(
            self.organizer_user
        )

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {
                "status": "EN_JUEGO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_organizer_cannot_delete_match(self):
        match = self.create_match()

        self.authenticate(
            self.organizer_user
        )

        response = self.client.delete(
            f"/api/matches/{match.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # -----------------------------
    # JUGADOR
    # -----------------------------

    def test_player_can_list_matches(self):
        self.authenticate(
            self.player_user
        )

        response = self.client.get(
            "/api/matches/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_player_cannot_create_match(self):
        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": self.player2.id,
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_update_match(self):
        match = self.create_match()

        self.authenticate(
            self.player_user
        )

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {
                "status": "FINALIZADO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_delete_match(self):
        match = self.create_match()

        self.authenticate(
            self.player_user
        )

        response = self.client.delete(
            f"/api/matches/{match.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # -----------------------------
    # REGLAS DE NEGOCIO
    # -----------------------------

    def test_elimination_match_requires_round(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": self.player2.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_ladder_match_does_not_use_round(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.ladder_category.id
                ),
                "player1": self.player1.id,
                "player2": self.player2.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertIsNone(
            response.data["round"]
        )

    def test_player_from_wrong_category_is_rejected(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": self.player3.id,
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_player_cannot_play_against_himself(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": self.player1.id,
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_winner_must_be_a_match_player(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": self.player2.id,
                "winner_player": self.player3.id,
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_bye_is_valid(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": None,
                "round": 1,
                "is_walkover": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_bye_cannot_be_walkover(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": None,
                "round": 1,
                "is_walkover": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_valid_walkover(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/matches/",
            {
                "competition_category": (
                    self.elimination_category.id
                ),
                "player1": self.player1.id,
                "player2": self.player2.id,
                "winner_player": self.player1.id,
                "round": 1,
                "is_walkover": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )
        
        
        
class MatchSetAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------
        # ROLES
        # -----------------------------

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

        # -----------------------------
        # USUARIOS
        # -----------------------------

        self.admin_user = User.objects.create_user(
            username="matchset_admin",
            password="TestPassword123!",
            email="matchset_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="matchset_organizer",
            password="TestPassword123!",
            email="matchset_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="matchset_player",
            password="TestPassword123!",
            email="matchset_player@tenis.cl",
            role=self.player_role,
        )

        # -----------------------------
        # CATEGORÍA
        # -----------------------------

        self.category = Category.objects.create(
            name="PRIMERA"
        )

        # -----------------------------
        # JUGADORES
        # -----------------------------

        self.player1_user = User.objects.create_user(
            username="matchset_player1",
            password="TestPassword123!",
            email="matchset_player1@tenis.cl",
            role=self.player_role,
        )

        self.player2_user = User.objects.create_user(
            username="matchset_player2",
            password="TestPassword123!",
            email="matchset_player2@tenis.cl",
            role=self.player_role,
        )

        self.player1 = Player.objects.create(
            user=self.player1_user,
            category=self.category,
            rut="41111111-1",
            first_name="Jugador",
            last_name="Uno",
        )

        self.player2 = Player.objects.create(
            user=self.player2_user,
            category=self.category,
            rut="42222222-2",
            first_name="Jugador",
            last_name="Dos",
        )

        # -----------------------------
        # COMPETENCIA
        # -----------------------------

        self.competition = Competition.objects.create(
            name="Torneo MatchSet",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

        # -----------------------------
        # COMPETITION CATEGORY
        # -----------------------------

        self.competition_category = (
            CompetitionCategory.objects.create(
                competition=self.competition,
                category=self.category,
                max_players=16,
                minimum_players=4,
            )
        )

        # -----------------------------
        # CANCHA
        # -----------------------------

        self.court = Court.objects.create(
            name="Cancha MatchSet 1"
        )

        # -----------------------------
        # MATCH
        # -----------------------------

        self.match = Match.objects.create(
            competition_category=self.competition_category,
            court=self.court,
            player1=self.player1,
            player2=self.player2,
            round=1,
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

        self.assertEqual(
            response.status_code,
            200
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

    # -----------------------------
    # AUTENTICACIÓN
    # -----------------------------

    def test_unauthenticated_user_cannot_list_match_sets(self):
        response = self.client.get(
            "/api/match-sets/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # -----------------------------
    # ADMINISTRADOR
    # -----------------------------

    def test_admin_can_list_match_sets(self):
        MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.get(
            "/api/match-sets/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_admin_can_create_match_set(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 6,
                "games_player2": 4,
                "is_super_tie_break": False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["set_number"],
            1
        )

        self.assertEqual(
            response.data["games_player1"],
            6
        )

        self.assertEqual(
            response.data["games_player2"],
            4
        )

    def test_admin_can_update_match_set(self):
        match_set = MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/match-sets/{match_set.id}/",
            {
                "games_player1": 6,
                "games_player2": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["games_player1"],
            6
        )

        self.assertEqual(
            response.data["games_player2"],
            2
        )

    def test_admin_can_delete_match_set(self):
        match_set = MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            f"/api/match-sets/{match_set.id}/"
        )

        self.assertEqual(
            response.status_code,
            204
        )

    # -----------------------------
    # ORGANIZADOR
    # -----------------------------

    def test_organizer_can_create_match_set(self):
        self.authenticate(
            self.organizer_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 6,
                "games_player2": 4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_can_update_match_set(self):
        match_set = MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.patch(
            f"/api/match-sets/{match_set.id}/",
            {
                "games_player1": 7,
                "games_player2": 5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_organizer_cannot_delete_match_set(self):
        match_set = MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.delete(
            f"/api/match-sets/{match_set.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # -----------------------------
    # JUGADOR
    # -----------------------------

    def test_player_can_list_match_sets(self):
        self.authenticate(
            self.player_user
        )

        response = self.client.get(
            "/api/match-sets/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_player_cannot_create_match_set(self):
        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 6,
                "games_player2": 4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_update_match_set(self):
        match_set = MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.patch(
            f"/api/match-sets/{match_set.id}/",
            {
                "games_player1": 7,
                "games_player2": 5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_delete_match_set(self):
        match_set = MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.delete(
            f"/api/match-sets/{match_set.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # -----------------------------
    # REGLAS DE MARCADOR
    # -----------------------------

    def test_valid_set_6_4(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 6,
                "games_player2": 4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_set_7_5(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 7,
                "games_player2": 5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_set_7_6(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 7,
                "games_player2": 6,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_invalid_set_6_5(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 6,
                "games_player2": 5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_invalid_set_8_6(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 8,
                "games_player2": 6,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # -----------------------------
    # SUPER TIE-BREAK
    # -----------------------------

    def test_valid_super_tie_break_10_8(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 3,
                "games_player1": 10,
                "games_player2": 8,
                "is_super_tie_break": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_super_tie_break_12_10(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 3,
                "games_player1": 12,
                "games_player2": 10,
                "is_super_tie_break": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_invalid_super_tie_break_10_9(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 3,
                "games_player1": 10,
                "games_player2": 9,
                "is_super_tie_break": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_super_tie_break_cannot_be_set_1(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 10,
                "games_player2": 8,
                "is_super_tie_break": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_super_tie_break_cannot_be_set_2(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 2,
                "games_player1": 10,
                "games_player2": 8,
                "is_super_tie_break": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # -----------------------------
    # VALIDACIONES ADICIONALES
    # -----------------------------

    def test_set_cannot_end_in_tie(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 6,
                "games_player2": 6,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_set_number_zero_is_invalid(self):
        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 0,
                "games_player1": 6,
                "games_player2": 4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_duplicate_set_number_is_rejected(self):
        MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match": self.match.id,
                "set_number": 1,
                "games_player1": 7,
                "games_player2": 5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )
        
class StandingAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # -----------------------------
        # ROLES
        # -----------------------------

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

        # -----------------------------
        # USUARIOS
        # -----------------------------

        self.admin_user = User.objects.create_user(
            username="standing_admin",
            password="TestPassword123!",
            email="standing_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="standing_organizer",
            password="TestPassword123!",
            email="standing_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="standing_player",
            password="TestPassword123!",
            email="standing_player@tenis.cl",
            role=self.player_role,
        )

        # -----------------------------
        # CATEGORÍA
        # -----------------------------

        self.category = Category.objects.create(
            name="PRIMERA"
        )

        # -----------------------------
        # JUGADORES
        # -----------------------------

        self.player1_user = User.objects.create_user(
            username="standing_player1",
            password="TestPassword123!",
            email="standing_player1@tenis.cl",
            role=self.player_role,
        )

        self.player2_user = User.objects.create_user(
            username="standing_player2",
            password="TestPassword123!",
            email="standing_player2@tenis.cl",
            role=self.player_role,
        )

        self.player1 = Player.objects.create(
            user=self.player1_user,
            category=self.category,
            rut="51111111-1",
            first_name="Jugador",
            last_name="Uno",
        )

        self.player2 = Player.objects.create(
            user=self.player2_user,
            category=self.category,
            rut="52222222-2",
            first_name="Jugador",
            last_name="Dos",
        )

        # -----------------------------
        # COMPETENCIA
        # -----------------------------

        self.competition = Competition.objects.create(
            name="Torneo Standing",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

        # -----------------------------
        # COMPETITION CATEGORY
        # -----------------------------

        self.competition_category = (
            CompetitionCategory.objects.create(
                competition=self.competition,
                category=self.category,
                max_players=16,
                minimum_players=4,
            )
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

        self.assertEqual(
            response.status_code,
            200
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

    def create_standing(self):

        return Standing.objects.create(
            competition_category=self.competition_category,
            player=self.player1,
        )

    # =================================================
    # AUTENTICACIÓN
    # =================================================

    def test_unauthenticated_user_cannot_list_standings(self):

        response = self.client.get(
            "/api/standings/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # =================================================
    # ADMINISTRADOR
    # =================================================

    def test_admin_can_list_standings(self):

        self.create_standing()

        self.authenticate(
            self.admin_user
        )

        response = self.client.get(
            "/api/standings/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_admin_can_create_standing(self):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/standings/",
            {
                "competition_category": (
                    self.competition_category.id
                ),
                "player": self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["matches_played"],
            0
        )

        self.assertEqual(
            response.data["matches_won"],
            0
        )

        self.assertEqual(
            response.data["points"],
            0
        )

        self.assertIsNone(
            response.data["position"]
        )

    def test_admin_can_update_standing(self):

        standing = self.create_standing()

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/standings/{standing.id}/",
            {
                "points": 100,
                "matches_won": 10,
                "position": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        # Los campos son read_only.
        # Por lo tanto permanecen en sus valores originales.

        self.assertEqual(
            response.data["points"],
            0
        )

        self.assertEqual(
            response.data["matches_won"],
            0
        )

        self.assertIsNone(
            response.data["position"]
        )

    def test_admin_can_delete_standing(self):

        standing = self.create_standing()

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            f"/api/standings/{standing.id}/"
        )

        self.assertEqual(
            response.status_code,
            204
        )

    # =================================================
    # ORGANIZADOR
    # =================================================

    def test_organizer_can_create_standing(self):

        self.authenticate(
            self.organizer_user
        )

        response = self.client.post(
            "/api/standings/",
            {
                "competition_category": (
                    self.competition_category.id
                ),
                "player": self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_can_update_standing(self):

        standing = self.create_standing()

        self.authenticate(
            self.organizer_user
        )

        response = self.client.patch(
            f"/api/standings/{standing.id}/",
            {
                "points": 100,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["points"],
            0
        )

    def test_organizer_cannot_delete_standing(self):

        standing = self.create_standing()

        self.authenticate(
            self.organizer_user
        )

        response = self.client.delete(
            f"/api/standings/{standing.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =================================================
    # JUGADOR
    # =================================================

    def test_player_can_list_standings(self):

        self.authenticate(
            self.player_user
        )

        response = self.client.get(
            "/api/standings/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_player_cannot_create_standing(self):

        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/standings/",
            {
                "competition_category": (
                    self.competition_category.id
                ),
                "player": self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_update_standing(self):

        standing = self.create_standing()

        self.authenticate(
            self.player_user
        )

        response = self.client.patch(
            f"/api/standings/{standing.id}/",
            {
                "points": 100,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_delete_standing(self):

        standing = self.create_standing()

        self.authenticate(
            self.player_user
        )

        response = self.client.delete(
            f"/api/standings/{standing.id}/"
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =================================================
    # REGLAS DE NEGOCIO
    # =================================================

    def test_player_wrong_category_is_rejected(self):

        User = get_user_model()

        second_category = Category.objects.create(
            name="SEGUNDA"
        )

        second_user = User.objects.create_user(
            username="standing_second",
            password="TestPassword123!",
            email="standing_second@tenis.cl",
            role=self.player_role,
        )

        second_player = Player.objects.create(
            user=second_user,
            category=second_category,
            rut="53333333-3",
            first_name="Jugador",
            last_name="Segunda",
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/standings/",
            {
                "competition_category": (
                    self.competition_category.id
                ),
                "player": second_player.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_duplicate_standing_is_rejected(self):

        self.create_standing()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/standings/",
            {
                "competition_category": (
                    self.competition_category.id
                ),
                "player": self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_statistics_are_read_only(self):

        standing = self.create_standing()

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/standings/{standing.id}/",
            {
                "matches_played": 50,
                "matches_won": 50,
                "matches_lost": 0,
                "sets_won": 100,
                "sets_lost": 0,
                "games_won": 500,
                "games_lost": 100,
                "points": 999,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["matches_played"],
            0
        )

        self.assertEqual(
            response.data["matches_won"],
            0
        )

        self.assertEqual(
            response.data["sets_won"],
            0
        )

        self.assertEqual(
            response.data["games_won"],
            0
        )

        self.assertEqual(
            response.data["points"],
            0
        )

    def test_position_is_read_only(self):

        standing = self.create_standing()

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/standings/{standing.id}/",
            {
                "position": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertIsNone(
            response.data["position"]
        )