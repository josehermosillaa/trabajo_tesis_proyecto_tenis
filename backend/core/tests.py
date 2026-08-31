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
    Standing,
    AuditLog
    )

from django.utils import timezone
from datetime import timedelta

from rest_framework.exceptions import ValidationError

from core.services.bracket_service import BracketService
from core.serializers import MatchSetSerializer

from django.urls import reverse
from rest_framework import status
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
    # TESTS CRUD
    # -----------------------------

    def test_list_players_authenticated(self):

        self.authenticate(
            self.admin_user
        )

        response = self.client.get(
            "/api/players/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_create_player(self):

        self.authenticate(
            self.admin_user
        )

        data = {
            "username": "juan.perez",
            "email": "juan.perez@test.cl",
            "password": "Temporal123!",
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

        self.assertEqual(
            response.data["username"],
            "juan.perez"
        )

        self.assertEqual(
            response.data["email"],
            "juan.perez@test.cl"
        )

        User = get_user_model()

        created_user = User.objects.get(
            username="juan.perez"
        )

        self.assertEqual(
            created_user.role.name,
            "Jugador"
        )

        self.assertTrue(
            created_user.check_password(
                "Temporal123!"
            )
        )

        self.assertTrue(
            Player.objects.filter(
                user=created_user
            ).exists()
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

        self.authenticate(
            self.admin_user
        )

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

        self.authenticate(
            self.admin_user
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
            200
        )

        self.assertEqual(
            response.data["phone"],
            "+56999999999"
        )

    def test_update_player_updates_user_data(self):

        player = Player.objects.create(
            user=self.admin_user,
            category=self.category,
            rut="45454545-4",
            first_name="Carlos",
            last_name="Pérez",
            birth_date="1992-03-10",
            phone="+56922222222",
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/players/{player.id}/",
            {
                "username": "carlos.actualizado",
                "email": "carlos.actualizado@test.cl",
                "first_name": "Carlos Andrés",
                "last_name": "Pérez Soto",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        player.refresh_from_db()
        player.user.refresh_from_db()

        self.assertEqual(
            player.user.username,
            "carlos.actualizado"
        )

        self.assertEqual(
            player.user.email,
            "carlos.actualizado@test.cl"
        )

        self.assertEqual(
            player.user.first_name,
            "Carlos Andrés"
        )

        self.assertEqual(
            player.user.last_name,
            "Pérez Soto"
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

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/players/",
            {
                "username": "otra.persona",
                "email": "otra.persona@test.cl",
                "password": "Temporal123!",
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

        User = get_user_model()

        self.assertFalse(
            User.objects.filter(
                username="otra.persona"
            ).exists()
        )

    def test_duplicate_username_not_allowed(self):

        User = get_user_model()

        User.objects.create_user(
            username="duplicado",
            password="TestPassword123!",
            email="duplicado@test.cl",
            role=self.player_role,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/players/",
            {
                "username": "duplicado",
                "email": "otro@test.cl",
                "password": "Temporal123!",
                "category": self.category.id,
                "rut": "13131313-1",
                "first_name": "Usuario",
                "last_name": "Duplicado",
                "birth_date": "1990-01-01",
                "phone": "+56911111111",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_duplicate_email_not_allowed(self):

        User = get_user_model()

        User.objects.create_user(
            username="usuario_email",
            password="TestPassword123!",
            email="correo@test.cl",
            role=self.player_role,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/players/",
            {
                "username": "otro.usuario",
                "email": "correo@test.cl",
                "password": "Temporal123!",
                "category": self.category.id,
                "rut": "14141414-1",
                "first_name": "Correo",
                "last_name": "Duplicado",
                "birth_date": "1990-01-01",
                "phone": "+56911111111",
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
            "username": "jugador.organizador",
            "email": "jugador.organizador@test.cl",
            "password": "Temporal123!",
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
            "username": "nuevo.jugador",
            "email": "nuevo.jugador@test.cl",
            "password": "Temporal123!",
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
    def test_player_phone_invalid_format(self):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/players/",
            {
                "username": "telefono.invalido",
                "email": "telefono@test.cl",
                "password": "Temporal123!",
                "category": self.category.id,
                "rut": "15151515-1",
                "first_name": "Telefono",
                "last_name": "Invalido",
                "birth_date": "1990-01-01",
                "phone": "+5691234",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_player_must_be_at_least_10_years_old(self):

        today = timezone.localdate()

        birth_date = today.replace(
            year=today.year - 5
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/players/",
            {
                "username": "jugador.menor",
                "email": "menor@test.cl",
                "password": "Temporal123!",
                "category": self.category.id,
                "rut": "16161616-1",
                "first_name": "Jugador",
                "last_name": "Menor",
                "birth_date": birth_date.isoformat(),
                "phone": "+56912345678",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
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

    def test_patch_minimum_players_cannot_exceed_maximum(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/competition-categories/"
            f"{competition_category.id}/",
            {
                "minimum_players": 20,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

    def test_patch_maximum_players_cannot_be_less_than_minimum(self):
        competition_category = (
            self.create_competition_category()
        )

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/competition-categories/"
            f"{competition_category.id}/",
            {
                "max_players": 2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400,
        )

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

        # =================================================
        # ROLES
        # =================================================

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

        # =================================================
        # USUARIOS
        # =================================================

        self.admin_user = User.objects.create_user(
            username="admin_registration",
            password="TestPassword123!",
            email="admin_registration@test.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="organizer_registration",
            password="TestPassword123!",
            email="organizer_registration@test.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="player_registration",
            password="TestPassword123!",
            email="player_registration@test.cl",
            role=self.player_role,
        )

        # =================================================
        # CATEGORÍAS
        # =================================================

        self.primera = Category.objects.create(
            name="PRIMERA"
        )

        self.segunda = Category.objects.create(
            name="SEGUNDA"
        )

        # =================================================
        # PLAYER DEL USUARIO JUGADOR
        # =================================================

        self.player = Player.objects.create(
            user=self.player_user,
            category=self.primera,
            rut="55555555-5",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1990-01-01",
            phone="+56955555555",
        )

        # =================================================
        # COMPETENCIA
        # =================================================

        today = timezone.localdate()

        self.competition = Competition.objects.create(
            name="Torneo Registration Test",
            type="ELIMINACION_DIRECTA",
            registration_deadline=(
                today + timedelta(days=3)
            ),
            start_date=(
                today + timedelta(days=7)
            ),
            end_date=(
                today + timedelta(days=21)
            ),
            status="PENDIENTE",
        )

        # =================================================
        # CATEGORÍAS DE LA COMPETENCIA
        # =================================================

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

    # =====================================================
    # HELPERS
    # =====================================================

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

    def create_registration(self):

        return Registration.objects.create(
            competition_category=(
                self.competition_primera
            ),
            player=self.player,
            status="PENDIENTE",
        )

    # =====================================================
    # AUTENTICACIÓN
    # =====================================================

    def test_unauthenticated_cannot_list_registrations(
        self
    ):

        response = self.client.get(
            "/api/registrations/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # =====================================================
    # ADMINISTRADOR
    # =====================================================

    def test_admin_can_list_registrations(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.get(
            "/api/registrations/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_admin_can_create_registration(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": self.player.id,
                "status": "PENDIENTE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["player"],
            self.player.id
        )

    def test_admin_can_update_registration(
        self
    ):

        registration = (
            self.create_registration()
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            (
                f"/api/registrations/"
                f"{registration.id}/"
            ),
            {
                "status": "CONFIRMADA",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["status"],
            "CONFIRMADA"
        )

    def test_admin_can_delete_registration(
        self
    ):

        registration = (
            self.create_registration()
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            (
                f"/api/registrations/"
                f"{registration.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            204
        )

        self.assertFalse(
            Registration.objects.filter(
                id=registration.id
            ).exists()
        )

    # =====================================================
    # ORGANIZADOR
    # =====================================================

    def test_organizer_can_create_registration(
        self
    ):

        self.authenticate(
            self.organizer_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": self.player.id,
                "status": "PENDIENTE",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_can_update_registration(
        self
    ):

        registration = (
            self.create_registration()
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.patch(
            (
                f"/api/registrations/"
                f"{registration.id}/"
            ),
            {
                "status": "CONFIRMADA",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["status"],
            "CONFIRMADA"
        )

    def test_organizer_cannot_delete_registration(
        self
    ):

        registration = (
            self.create_registration()
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.delete(
            (
                f"/api/registrations/"
                f"{registration.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =====================================================
    # JUGADOR - LECTURA
    # =====================================================

    def test_player_can_list_registrations(
        self
    ):

        self.authenticate(
            self.player_user
        )

        response = self.client.get(
            "/api/registrations/"
        )

        self.assertEqual(
            response.status_code,
            200
        )

    # =====================================================
    # JUGADOR - AUTOINSCRIPCIÓN
    # =====================================================

    def test_player_can_register_himself(
        self
    ):

        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["player"],
            self.player.id
        )

        self.assertEqual(
            response.data["status"],
            "CONFIRMADA"
        )

        self.assertIsNone(
            response.data["seed"]
        )

        self.assertTrue(
            Registration.objects.filter(
                competition_category=(
                    self.competition_primera
                ),
                player=self.player,
            ).exists()
        )

    def test_player_cannot_register_another_player(
        self
    ):

        User = get_user_model()

        other_user = User.objects.create_user(
            username="other_player",
            password="TestPassword123!",
            email="other_player@test.cl",
            role=self.player_role,
        )

        other_player = Player.objects.create(
            user=other_user,
            category=self.primera,
            rut="12345678-5",
            first_name="Otro",
            last_name="Jugador",
            birth_date="1990-01-01",
            phone="+56912345678",
        )

        self.authenticate(
            self.player_user
        )

        # Intenta manipular el payload enviando
        # el ID de otro jugador.
        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": other_player.id,
            },
            format="json",
        )

        # La petición puede realizarse,
        # pero Django debe sustituir el player
        # por el asociado al usuario autenticado.
        self.assertEqual(
            response.status_code,
            201
        )

        self.assertEqual(
            response.data["player"],
            self.player.id
        )

        self.assertFalse(
            Registration.objects.filter(
                competition_category=(
                    self.competition_primera
                ),
                player=other_player,
            ).exists()
        )

        self.assertTrue(
            Registration.objects.filter(
                competition_category=(
                    self.competition_primera
                ),
                player=self.player,
            ).exists()
        )

    def test_player_cannot_choose_status_or_seed(
        self
    ):

        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "status": "CONFIRMADA",
                "seed": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        # El backend debe forzar estos valores.
        self.assertEqual(
            response.data["status"],
            "CONFIRMADA"
        )

        self.assertIsNone(
            response.data["seed"]
        )

    def test_player_cannot_register_in_different_category(
        self
    ):

        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_segunda.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_player_cannot_register_after_deadline(
        self
    ):

        self.competition.status = (
            "ABIERTA"
        )

        self.competition.registration_deadline = (
            timezone.localdate()
            - timedelta(days=1)
        )

        self.competition.save()

        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_player_cannot_register_when_competition_in_progress(
        self
    ):

        self.competition.status = (
            "EN_CURSO"
        )

        self.competition.save()

        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_player_cannot_update_registration(
        self
    ):

        registration = (
            self.create_registration()
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.patch(
            (
                f"/api/registrations/"
                f"{registration.id}/"
            ),
            {
                "status": "CONFIRMADA",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_delete_registration(
        self
    ):

        registration = (
            self.create_registration()
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.delete(
            (
                f"/api/registrations/"
                f"{registration.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =====================================================
    # VALIDACIONES DE NEGOCIO
    # =====================================================

    def test_cannot_register_player_in_wrong_category(
        self
    ):

        self.authenticate(
            self.admin_user
        )

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

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cannot_duplicate_registration(
        self
    ):

        self.create_registration()

        self.authenticate(
            self.admin_user
        )

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

        self.assertEqual(
            response.status_code,
            400
        )

    def test_registration_date_is_generated_automatically(
        self
    ):

        self.authenticate(
            self.admin_user
        )

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

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertIsNotNone(
            response.data[
                "registration_date"
            ]
        )

    def test_registration_date_cannot_be_modified(
        self
    ):

        registration = (
            self.create_registration()
        )

        original_date = (
            registration.registration_date
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            (
                f"/api/registrations/"
                f"{registration.id}/"
            ),
            {
                "registration_date": (
                    "2000-01-01T00:00:00Z"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        registration.refresh_from_db()

        self.assertEqual(
            registration.registration_date,
            original_date,
        )

    # =====================================================
    # ESTADO DE LA COMPETENCIA
    # =====================================================

    def test_admin_can_register_when_competition_in_progress(
        self
    ):

        self.competition.status = (
            "EN_CURSO"
        )

        self.competition.save()

        self.authenticate(
            self.admin_user
        )

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

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_cannot_register_when_competition_in_progress(
        self
    ):

        self.competition.status = (
            "EN_CURSO"
        )

        self.competition.save()

        self.authenticate(
            self.organizer_user
        )

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

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cannot_register_when_competition_finished(
        self
    ):

        self.competition.status = (
            "FINALIZADA"
        )

        self.competition.save()

        self.authenticate(
            self.admin_user
        )

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

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cannot_register_when_competition_cancelled(
        self
    ):

        self.competition.status = (
            "CANCELADA"
        )

        self.competition.save()

        self.authenticate(
            self.admin_user
        )

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

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # FECHA LÍMITE
    # =====================================================

    def test_admin_can_register_after_deadline(
        self
    ):

        self.competition.registration_deadline = (
            timezone.localdate()
            - timedelta(days=1)
        )

        self.competition.save()

        self.authenticate(
            self.admin_user
        )

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

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_cannot_register_after_deadline(
        self
    ):

        self.competition.registration_deadline = (
            timezone.localdate()
            - timedelta(days=1)
        )

        self.competition.save()

        self.authenticate(
            self.organizer_user
        )

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

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # CUPOS
    # =====================================================

    def test_cannot_register_when_category_is_full(
        self
    ):

        # Dejamos capacidad de solo un jugador.
        self.competition_primera.max_players = 1
        self.competition_primera.minimum_players = 1

        self.competition_primera.save()

        self.create_registration()

        User = get_user_model()

        second_user = User.objects.create_user(
            username="second_player",
            password="TestPassword123!",
            email="second_player@test.cl",
            role=self.player_role,
        )

        second_player = Player.objects.create(
            user=second_user,
            category=self.primera,
            rut="11111111-1",
            first_name="Segundo",
            last_name="Jugador",
            birth_date="1990-01-01",
            phone="+56911111111",
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": second_player.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cancelled_registration_does_not_use_slot(
        self
    ):

        self.competition_primera.max_players = 1
        self.competition_primera.minimum_players = 1

        self.competition_primera.save()

        Registration.objects.create(
            competition_category=(
                self.competition_primera
            ),
            player=self.player,
            status="CANCELADA",
        )

        User = get_user_model()

        second_user = User.objects.create_user(
            username="available_player",
            password="TestPassword123!",
            email="available_player@test.cl",
            role=self.player_role,
        )

        second_player = Player.objects.create(
            user=second_user,
            category=self.primera,
            rut="11111111-1",
            first_name="Jugador",
            last_name="Disponible",
            birth_date="1990-01-01",
            phone="+56911111111",
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/registrations/",
            {
                "competition_category": (
                    self.competition_primera.id
                ),
                "player": second_player.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    # =====================================================
    # INFORMACIÓN DE CUPOS
    # =====================================================

    def test_competition_category_returns_slot_information(
        self
    ):

        self.create_registration()

        self.authenticate(
            self.admin_user
        )

        response = self.client.get(
            (
                "/api/competition-categories/"
                f"{self.competition_primera.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertEqual(
            response.data["occupied_slots"],
            1
        )

        self.assertEqual(
            response.data["available_slots"],
            15
        )

        self.assertEqual(
            len(
                response.data[
                    "registered_players"
                ]
            ),
            1
        )

        registered_player = (
            response.data[
                "registered_players"
            ][0]
        )

        self.assertEqual(
            registered_player["id"],
            self.player.id
        )

        self.assertEqual(
            registered_player[
                "first_name"
            ],
            "Jugador"
        )

        self.assertEqual(
            registered_player[
                "last_name"
            ],
            "Prueba"
        )

        self.assertEqual(
            registered_player["status"],
            "PENDIENTE"
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

        # =================================================
        # ROLES
        # =================================================

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

        # =================================================
        # USUARIOS
        # =================================================

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

        # =================================================
        # CATEGORÍAS
        # =================================================

        self.primera = Category.objects.create(
            name="PRIMERA"
        )

        self.segunda = Category.objects.create(
            name="SEGUNDA"
        )

        # =================================================
        # USUARIOS DE LOS JUGADORES
        # =================================================

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

        # =================================================
        # PLAYERS
        # =================================================

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

        # =================================================
        # COMPETENCIAS
        # =================================================

        self.competition_elimination = (
            Competition.objects.create(
                name="Torneo Match Eliminación",
                type="ELIMINACION_DIRECTA",
                start_date="2026-09-01",
                end_date="2026-09-15",
                registration_deadline="2026-08-28",
            )
        )

        self.competition_ladder = (
            Competition.objects.create(
                name="Torneo Match Escalerilla",
                type="ESCALERILLA",
                start_date="2026-10-01",
                end_date="2026-10-15",
                registration_deadline="2026-09-28",
            )
        )

        # =================================================
        # COMPETITION CATEGORIES
        # =================================================

        self.elimination_category = (
            CompetitionCategory.objects.create(
                competition=(
                    self.competition_elimination
                ),
                category=self.primera,
                max_players=16,
                minimum_players=4,
            )
        )

        self.ladder_category = (
            CompetitionCategory.objects.create(
                competition=(
                    self.competition_ladder
                ),
                category=self.primera,
                max_players=16,
                minimum_players=2,
            )
        )

        # =================================================
        # INSCRIPCIONES CONFIRMADAS
        # =================================================

        self.registration_player1_elimination = (
            Registration.objects.create(
                competition_category=(
                    self.elimination_category
                ),
                player=self.player1,
                status="CONFIRMADA",
            )
        )

        self.registration_player2_elimination = (
            Registration.objects.create(
                competition_category=(
                    self.elimination_category
                ),
                player=self.player2,
                status="CONFIRMADA",
            )
        )

        self.registration_player1_ladder = (
            Registration.objects.create(
                competition_category=(
                    self.ladder_category
                ),
                player=self.player1,
                status="CONFIRMADA",
            )
        )

        self.registration_player2_ladder = (
            Registration.objects.create(
                competition_category=(
                    self.ladder_category
                ),
                player=self.player2,
                status="CONFIRMADA",
            )
        )

        # =================================================
        # CANCHA
        # =================================================

        self.court = Court.objects.create(
            name="Cancha Match 1"
        )

    # =====================================================
    # HELPERS
    # =====================================================

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
            competition_category=(
                self.elimination_category
            ),
            court=self.court,
            player1=self.player1,
            player2=self.player2,
            round=1,
        )

    # =====================================================
    # AUTENTICACIÓN
    # =====================================================

    def test_unauthenticated_user_cannot_list_matches(
        self
    ):

        response = self.client.get(
            "/api/matches/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # =====================================================
    # ADMINISTRADOR
    # =====================================================

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
                "winner_player": (
                    self.player1.id
                ),
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

    def test_admin_can_schedule_programmed_match(self):

        match = self.create_match()

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {
                "scheduled_date_time": "2026-09-03T19:30:00-04:00",
                "court": self.court.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["court"], self.court.id)
        self.assertIsNotNone(response.data["scheduled_date_time"])

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

    # =====================================================
    # ORGANIZADOR
    # =====================================================

    def test_organizer_can_create_match(
        self
    ):

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

    def test_organizer_can_update_match(
        self
    ):

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

    def test_organizer_can_schedule_programmed_match(self):

        match = self.create_match()

        self.authenticate(self.organizer_user)

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {
                "scheduled_date_time": "2026-09-04T18:00:00-04:00",
                "court": self.court.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_organizer_cannot_delete_match(
        self
    ):

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

    # =====================================================
    # JUGADOR
    # =====================================================

    def test_player_can_list_matches(
        self
    ):

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

    def test_player_cannot_create_match(
        self
    ):

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

    def test_player_cannot_update_match(
        self
    ):

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

    def test_player_cannot_schedule_match(self):

        match = self.create_match()

        self.authenticate(self.player_user)

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {
                "scheduled_date_time": "2026-09-03T19:30:00-04:00",
                "court": self.court.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_schedule_match_without_both_players(self):

        match = self.create_match()
        match.player2 = None
        match.save(update_fields=["player2"])

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {
                "scheduled_date_time": "2026-09-03T19:30:00-04:00",
                "court": self.court.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_cannot_edit_schedule_of_finalized_match(self):

        match = self.create_match()
        match.status = Match.Status.FINALIZADO
        match.winner_player = self.player1
        match.save(update_fields=["status", "winner_player"])

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {"court": self.court.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_cannot_edit_schedule_of_cancelled_match(self):

        match = self.create_match()
        match.status = Match.Status.CANCELADO
        match.save(update_fields=["status"])

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {"court": self.court.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_cannot_edit_schedule_of_match_in_progress(self):

        match = self.create_match()
        match.status = Match.Status.EN_JUEGO
        match.save(update_fields=["status"])

        self.authenticate(self.admin_user)

        response = self.client.patch(
            f"/api/matches/{match.id}/",
            {"court": self.court.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_player_cannot_delete_match(
        self
    ):

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

    # =====================================================
    # REGLAS DE INSCRIPCIÓN
    # =====================================================

    def test_pending_player_cannot_play_match(
        self
    ):

        self.registration_player2_elimination.status = (
            "PENDIENTE"
        )

        self.registration_player2_elimination.save()

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
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cancelled_player_cannot_play_match(
        self
    ):

        self.registration_player2_elimination.status = (
            "CANCELADA"
        )

        self.registration_player2_elimination.save()

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
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # MODALIDAD / RONDA
    # =====================================================

    def test_elimination_match_requires_round(
        self
    ):

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

    def test_ladder_match_does_not_use_round(
        self
    ):

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

    def test_ladder_match_rejects_round(
        self
    ):

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
                "round": 1,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # CATEGORÍA
    # =====================================================

    def test_player_from_wrong_category_is_rejected(
        self
    ):

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

    # =====================================================
    # MISMO JUGADOR
    # =====================================================

    def test_player_cannot_play_against_himself(
        self
    ):

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

    # =====================================================
    # GANADOR
    # =====================================================

    def test_winner_must_be_a_match_player(
        self
    ):

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
                "status": "FINALIZADO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_finished_match_requires_winner(
        self
    ):

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
                "round": 1,
                "status": "FINALIZADO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_programmed_match_cannot_have_winner(
        self
    ):

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
                "status": "PROGRAMADO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_in_progress_match_cannot_have_winner(
        self
    ):

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
                "status": "EN_JUEGO",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # BYE
    # =====================================================

    def test_bye_is_valid(
        self
    ):

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

    def test_bye_cannot_be_walkover(
        self
    ):

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

    # =====================================================
    # WALKOVER
    # =====================================================

    def test_walkover_requires_winner(
        self
    ):

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
                "round": 1,
                "is_walkover": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_valid_walkover(
        self
    ):

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
                "winner_player": (
                    self.player1.id
                ),
                "round": 1,
                "is_walkover": True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.assertTrue(
            response.data["is_walkover"]
        )

        self.assertEqual(
            response.data["winner_player"],
            self.player1.id
        )

        self.assertEqual(
            response.data["status"],
            "FINALIZADO"
        )     
        
class MatchSetAPITest(TestCase):

    def setUp(self):

        self.client = APIClient()

        # =================================================
        # ROLES
        # =================================================

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

        # =================================================
        # USUARIOS
        # =================================================

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

        # =================================================
        # CATEGORÍA
        # =================================================

        self.category = Category.objects.create(
            name="PRIMERA"
        )

        # =================================================
        # JUGADORES
        # =================================================

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

        # =================================================
        # COMPETENCIA
        # =================================================

        self.competition = Competition.objects.create(
            name="Torneo MatchSet",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

        # =================================================
        # COMPETITION CATEGORY
        # =================================================

        self.competition_category = (
            CompetitionCategory.objects.create(
                competition=self.competition,
                category=self.category,
                max_players=16,
                minimum_players=4,
            )
        )

        # =================================================
        # INSCRIPCIONES CONFIRMADAS
        # =================================================

        Registration.objects.create(
            competition_category=(
                self.competition_category
            ),
            player=self.player1,
            status="CONFIRMADA",
        )

        Registration.objects.create(
            competition_category=(
                self.competition_category
            ),
            player=self.player2,
            status="CONFIRMADA",
        )

        # =================================================
        # CANCHA
        # =================================================

        self.court = Court.objects.create(
            name="Cancha MatchSet 1"
        )

        # =================================================
        # MATCH
        # =================================================

        self.match = Match.objects.create(
            competition_category=(
                self.competition_category
            ),
            court=self.court,
            player1=self.player1,
            player2=self.player2,
            round=1,
        )

    # =====================================================
    # HELPERS
    # =====================================================

    def authenticate(
        self,
        user
    ):

        response = self.client.post(
            "/api/token/",
            {
                "username": user.username,
                "password": (
                    "TestPassword123!"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer "
                f"{response.data['access']}"
            )
        )

    def create_set_1(
        self,
        games1=6,
        games2=4,
    ):

        return MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=games1,
            games_player2=games2,
        )

    def create_set_2(
        self,
        games1=6,
        games2=4,
    ):

        return MatchSet.objects.create(
            match=self.match,
            set_number=2,
            games_player1=games1,
            games_player2=games2,
        )

    def create_split_sets(self):

        self.create_set_1(
            6,
            4,
        )

        self.create_set_2(
            3,
            6,
        )

    # =====================================================
    # AUTENTICACIÓN
    # =====================================================

    def test_unauthenticated_user_cannot_list_match_sets(
        self
    ):

        response = self.client.get(
            "/api/match-sets/"
        )

        self.assertEqual(
            response.status_code,
            401
        )

    # =====================================================
    # ADMINISTRADOR
    # =====================================================

    def test_admin_can_list_match_sets(
        self
    ):

        self.create_set_1()

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

    def test_admin_can_create_match_set(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    4,

                "is_super_tie_break":
                    False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_admin_can_update_match_set(
        self
    ):

        match_set = (
            self.create_set_1()
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            (
                f"/api/match-sets/"
                f"{match_set.id}/"
            ),
            {
                "games_player1":
                    6,

                "games_player2":
                    2,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_admin_can_delete_match_set(
        self
    ):

        match_set = (
            self.create_set_1()
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            (
                f"/api/match-sets/"
                f"{match_set.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            204
        )

    # =====================================================
    # ORGANIZADOR
    # =====================================================

    def test_organizer_can_create_match_set(
        self
    ):

        self.authenticate(
            self.organizer_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_organizer_can_update_match_set(
        self
    ):

        match_set = (
            self.create_set_1()
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.patch(
            (
                f"/api/match-sets/"
                f"{match_set.id}/"
            ),
            {
                "games_player1":
                    7,

                "games_player2":
                    5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_organizer_cannot_delete_match_set(
        self
    ):

        match_set = (
            self.create_set_1()
        )

        self.authenticate(
            self.organizer_user
        )

        response = self.client.delete(
            (
                f"/api/match-sets/"
                f"{match_set.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =====================================================
    # JUGADOR
    # =====================================================

    def test_player_can_list_match_sets(
        self
    ):

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

    def test_player_cannot_create_match_set(
        self
    ):

        self.authenticate(
            self.player_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_update_match_set(
        self
    ):

        match_set = (
            self.create_set_1()
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.patch(
            (
                f"/api/match-sets/"
                f"{match_set.id}/"
            ),
            {
                "games_player1":
                    7,

                "games_player2":
                    5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_player_cannot_delete_match_set(
        self
    ):

        match_set = (
            self.create_set_1()
        )

        self.authenticate(
            self.player_user
        )

        response = self.client.delete(
            (
                f"/api/match-sets/"
                f"{match_set.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            403
        )

    # =====================================================
    # SET NORMAL
    # =====================================================

    def test_valid_set_6_4(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_set_7_5(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    7,

                "games_player2":
                    5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_set_7_6(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    7,

                "games_player2":
                    6,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_invalid_set_6_5(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_invalid_set_8_6(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    8,

                "games_player2":
                    6,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # ORDEN DE SETS
    # =====================================================

    def test_set_2_requires_set_1(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    2,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_set_3_requires_first_two_sets(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    10,

                "games_player2":
                    8,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # SUPER TIE-BREAK
    # =====================================================

    def test_valid_super_tie_break_10_2(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    10,

                "games_player2":
                    2,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_super_tie_break_10_8(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    10,

                "games_player2":
                    8,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_super_tie_break_11_9(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    11,

                "games_player2":
                    9,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_valid_super_tie_break_12_10(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    12,

                "games_player2":
                    10,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

    def test_invalid_super_tie_break_10_9(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    10,

                "games_player2":
                    9,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # NUEVO:
    # El partido habría terminado 10-8.
    def test_invalid_super_tie_break_11_8(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    11,

                "games_player2":
                    8,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # NUEVO:
    # El caso que detectaste manualmente.
    def test_invalid_super_tie_break_12_2(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    12,

                "games_player2":
                    2,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # NUEVO:
    # Si llegó a 9, debe ganar exactamente
    # por diferencia de 2.
    def test_invalid_super_tie_break_12_9(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    12,

                "games_player2":
                    9,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_super_tie_break_cannot_be_set_1(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    10,

                "games_player2":
                    8,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_third_set_must_be_super_tie_break(
        self
    ):

        self.create_split_sets()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    6,

                "games_player2":
                    4,

                "is_super_tie_break":
                    False,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_third_set_not_allowed_after_two_zero(
        self
    ):

        self.create_set_1(
            6,
            4,
        )

        self.create_set_2(
            6,
            3,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    10,

                "games_player2":
                    8,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # GANADOR AUTOMÁTICO
    # =====================================================

    def test_match_finishes_automatically_two_zero(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response1 = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.assertEqual(
            response1.status_code,
            201
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "EN_JUEGO"
        )

        response2 = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    2,

                "games_player1":
                    6,

                "games_player2":
                    3,
            },
            format="json",
        )

        self.assertEqual(
            response2.status_code,
            201
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "FINALIZADO"
        )

        self.assertEqual(
            self.match.winner_player,
            self.player1
        )

    def test_match_finishes_automatically_with_super_tie_break(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    2,

                "games_player1":
                    3,

                "games_player2":
                    6,
            },
            format="json",
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    3,

                "games_player1":
                    8,

                "games_player2":
                    10,

                "is_super_tie_break":
                    True,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "FINALIZADO"
        )

        self.assertEqual(
            self.match.winner_player,
            self.player2
        )

    # =====================================================
    # DELETE Y RECÁLCULO
    # =====================================================

    def test_deleting_set_recalculates_match(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response1 = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        response2 = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    2,

                "games_player1":
                    6,

                "games_player2":
                    3,
            },
            format="json",
        )

        self.assertEqual(
            response1.status_code,
            201
        )

        self.assertEqual(
            response2.status_code,
            201
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "FINALIZADO"
        )

        second_set_id = (
            response2.data["id"]
        )

        delete_response = (
            self.client.delete(
                (
                    f"/api/match-sets/"
                    f"{second_set_id}/"
                )
            )
        )

        self.assertEqual(
            delete_response.status_code,
            204
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            "EN_JUEGO"
        )

        self.assertIsNone(
            self.match.winner_player
        )

    # =====================================================
    # BYE / WALKOVER
    # =====================================================

    def test_sets_cannot_be_created_for_bye(
        self
    ):

        bye_match = Match.objects.create(
            competition_category=(
                self.competition_category
            ),
            court=self.court,
            player1=self.player1,
            player2=None,
            round=1,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    bye_match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_sets_cannot_be_created_for_walkover(
        self
    ):

        walkover_match = (
            Match.objects.create(
                competition_category=(
                    self.competition_category
                ),
                court=self.court,
                player1=self.player1,
                player2=self.player2,
                winner_player=self.player1,
                round=1,
                is_walkover=True,
                status="FINALIZADO",
            )
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    walkover_match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    0,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    # =====================================================
    # OTRAS VALIDACIONES
    # =====================================================

    def test_set_cannot_end_in_tie(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    6,

                "games_player2":
                    6,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_set_number_zero_is_invalid(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    0,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_set_number_four_is_invalid(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    4,

                "games_player1":
                    6,

                "games_player2":
                    4,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_duplicate_set_number_is_rejected(
        self
    ):

        self.create_set_1()

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    1,

                "games_player1":
                    7,

                "games_player2":
                    5,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            400
        )

    def test_cannot_delete_set_2_when_set_3_exists(
        self
    ):
        """
        No se puede eliminar el Set 2
        si ya existe un Set 3.
        """

        match = Match.objects.create(
            competition_category=(
                self.competition_category
            ),
            player1=self.player1,
            player2=self.player2,
            round=1,
            status=(
                Match.Status.PROGRAMADO
            ),
        )

        MatchSet.objects.create(
            match=match,
            set_number=1,
            games_player1=6,
            games_player2=4,
            is_super_tie_break=False,
        )

        set2 = MatchSet.objects.create(
            match=match,
            set_number=2,
            games_player1=4,
            games_player2=6,
            is_super_tie_break=False,
        )

        set3 = MatchSet.objects.create(
            match=match,
            set_number=3,
            games_player1=10,
            games_player2=8,
            is_super_tie_break=True,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.delete(
            (
                f"/api/match-sets/"
                f"{set2.id}/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertTrue(
            MatchSet.objects.filter(
                pk=set2.id
            ).exists()
        )

        self.assertTrue(
            MatchSet.objects.filter(
                pk=set3.id
            ).exists()
        )

        self.assertIn(
            "detail",
            response.data,
        )

        self.assertIn(
            "sets posteriores",
            str(
                response.data[
                    "detail"
                ]
            ),
        )
        
    def test_can_delete_last_registered_set(
            self
        ):
            """
            Sí se puede eliminar el último
            set registrado del partido.
            """

            match = Match.objects.create(
                competition_category=(
                    self.competition_category
                ),
                player1=self.player1,
                player2=self.player2,
                round=1,
                status=(
                    Match.Status.PROGRAMADO
                ),
            )

            set1 = MatchSet.objects.create(
                match=match,
                set_number=1,
                games_player1=6,
                games_player2=4,
                is_super_tie_break=False,
            )

            set2 = MatchSet.objects.create(
                match=match,
                set_number=2,
                games_player1=4,
                games_player2=6,
                is_super_tie_break=False,
            )

            set3 = MatchSet.objects.create(
                match=match,
                set_number=3,
                games_player1=10,
                games_player2=8,
                is_super_tie_break=True,
            )

            self.authenticate(
                self.admin_user
            )

            response = self.client.delete(
                (
                    f"/api/match-sets/"
                    f"{set3.id}/"
                )
            )

            self.assertEqual(
                response.status_code,
                status.HTTP_204_NO_CONTENT,
            )

            self.assertFalse(
                MatchSet.objects.filter(
                    pk=set3.id
                ).exists()
            )

            self.assertTrue(
                MatchSet.objects.filter(
                    pk=set1.id
                ).exists()
            )

            self.assertTrue(
                MatchSet.objects.filter(
                    pk=set2.id
                ).exists()
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
        

class AuditLogAPITest(TestCase):

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
            username="audit_admin",
            password="TestPassword123!",
            email="audit_admin@tenis.cl",
            role=self.admin_role,
        )

        self.organizer_user = User.objects.create_user(
            username="audit_organizer",
            password="TestPassword123!",
            email="audit_organizer@tenis.cl",
            role=self.organizer_role,
        )

        self.player_user = User.objects.create_user(
            username="audit_player",
            password="TestPassword123!",
            email="audit_player@tenis.cl",
            role=self.player_role,
        )

        # -----------------------------
        # CATEGORÍA
        # -----------------------------

        self.category = Category.objects.create(
            name="PRIMERA"
        )

        # -----------------------------
        # JUGADOR EXISTENTE
        # -----------------------------

        self.player = Player.objects.create(
            user=self.player_user,
            category=self.category,
            rut="61111111-1",
            first_name="Jugador",
            last_name="Prueba",
            birth_date="1995-05-20",
            phone="+56911111111",
        )

        # -----------------------------
        # COMPETENCIA
        # -----------------------------

        self.competition = Competition.objects.create(
            name="Torneo Auditoria",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
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

    # =================================================
    # CREATE
    # =================================================

    def test_audit_log_created_on_player_create(self):

        self.authenticate(
            self.admin_user
        )

        User = get_user_model()

        new_player_user = User.objects.create_user(
            username="audit_new_player",
            password="TestPassword123!",
            email="audit_new_player@tenis.cl",
            role=self.player_role,
        )

        response = self.client.post(
            "/api/players/",
            {
                "user": new_player_user.id,
                "category": self.category.id,
                "rut": "62222222-2",
                "first_name": "Nuevo",
                "last_name": "Jugador",
                "birth_date": "1990-01-01",
                "phone": "+56922222222",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            201
        )

        log = AuditLog.objects.latest(
            "id"
        )

        self.assertEqual(
            log.user_id,
            self.admin_user.id
        )

        self.assertEqual(
            log.username,
            self.admin_user.username
        )

        self.assertEqual(
            log.user_name,
            self.admin_user.get_full_name()
            or self.admin_user.username
        )

        self.assertEqual(
            log.entity_name,
            "Player"
        )

        self.assertEqual(
            log.entity_id,
            response.data["id"]
        )

        self.assertEqual(
            log.action,
            "CREATE"
        )
    # =================================================
    # UPDATE
    # =================================================

    def test_audit_log_created_on_player_update(self):

        self.authenticate(
            self.admin_user
        )

        initial_count = AuditLog.objects.count()

        response = self.client.patch(
            f"/api/players/{self.player.id}/",
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
            AuditLog.objects.count(),
            initial_count + 1
        )

        log = AuditLog.objects.latest(
            "id"
        )

        self.assertEqual(
            log.user_id,
            self.admin_user.id
        )

        self.assertEqual(
            log.username,
            self.admin_user.username
        )

        self.assertEqual(
            log.entity_name,
            "Player"
        )

        self.assertEqual(
            log.entity_id,
            self.player.id
        )

        self.assertEqual(
            log.action,
            "UPDATE"
        )

    # =================================================
    # DELETE
    # =================================================

    def test_audit_log_created_on_player_delete(self):

        self.authenticate(
            self.admin_user
        )

        player_id = self.player.id

        initial_count = AuditLog.objects.count()

        response = self.client.delete(
            f"/api/players/{player_id}/"
        )

        self.assertEqual(
            response.status_code,
            204
        )

        self.assertEqual(
            AuditLog.objects.count(),
            initial_count + 1
        )

        log = AuditLog.objects.latest(
            "id"
        )

        self.assertEqual(
            log.user_id,
            self.admin_user.id
        )

        self.assertEqual(
            log.username,
            self.admin_user.username
        )

        self.assertEqual(
            log.entity_name,
            "Player"
        )

        self.assertEqual(
            log.entity_id,
            player_id
        )

        self.assertEqual(
            log.action,
            "DELETE"
        )

    # =================================================
    # IDENTIDAD HISTÓRICA
    # =================================================

    def test_audit_log_preserves_user_identity_after_delete(self):

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/players/{self.player.id}/",
            {
                "phone": "+56988888888",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        log = AuditLog.objects.latest(
            "id"
        )

        username = self.admin_user.username

        user_name = (
            self.admin_user.get_full_name()
            or self.admin_user.username
        )

        self.admin_user.delete()

        log.refresh_from_db()

        self.assertIsNone(
            log.user_id
        )

        self.assertEqual(
            log.username,
            username
        )

        self.assertEqual(
            log.user_name,
            user_name
        )

    # =================================================
    # CREATED_AT
    # =================================================

    def test_audit_log_has_created_at(self):

        self.authenticate(
            self.admin_user
        )

        response = self.client.patch(
            f"/api/players/{self.player.id}/",
            {
                "phone": "+56977777777",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            200
        )

        log = AuditLog.objects.latest(
            "id"
        )

        self.assertIsNotNone(
            log.created_at
        )

    # =================================================
    # NO AUTENTICADO
    # =================================================

    def test_unauthenticated_user_cannot_modify_player_and_create_audit(self):

        initial_count = AuditLog.objects.count()

        response = self.client.patch(
            f"/api/players/{self.player.id}/",
            {
                "phone": "+56966666666",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            401
        )

        self.assertEqual(
            AuditLog.objects.count(),
            initial_count
        )
        
class BracketServiceTest(TestCase):

    def setUp(self):

        self.admin_role = Role.objects.create(
            name="Administrador"
        )

        self.player_role = Role.objects.create(
            name="Jugador"
        )

        User = get_user_model()

        self.category = Category.objects.create(
            name="PRIMERA"
        )

        self.competition = Competition.objects.create(
            name="Torneo Bracket",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-30",
            registration_deadline="2026-08-28",
        )

        self.competition_category = (
            CompetitionCategory.objects.create(
                competition=self.competition,
                category=self.category,
                max_players=64,
                minimum_players=2,
            )
        )

        self.users = []
        self.players = []

    # =====================================================
    # HELPERS
    # =====================================================

    def create_players(
        self,
        amount,
        with_seeds=False,
    ):

        created = []

        start_index = (
            len(self.players) + 1
        )

        for index in range(
            start_index,
            start_index + amount,
        ):

            user = (
                get_user_model()
                .objects
                .create_user(
                    username=(
                        f"bracket_player_{index}"
                    ),
                    password=(
                        "TestPassword123!"
                    ),
                    email=(
                        f"bracket_player_{index}"
                        "@tenis.cl"
                    ),
                    role=self.player_role,
                )
            )

            player = Player.objects.create(
                user=user,
                category=self.category,
                rut=(
                    f"{10000000 + index}-K"
                ),
                first_name="Jugador",
                last_name=str(index),
            )

            seed = (
                index
                if with_seeds
                else None
            )

            registration = (
                Registration.objects.create(
                    competition_category=(
                        self.competition_category
                    ),
                    player=player,
                    status="CONFIRMADA",
                    seed=seed,
                )
            )

            self.users.append(
                user
            )

            self.players.append(
                player
            )

            created.append(
                registration
            )

        return created

    def get_first_round_matches(self):

        return list(
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=1,
            ).order_by(
                "bracket_position"
            )
        )

    def get_seed_pairs_from_first_round(self):

        registrations = {
            registration.player_id:
                registration.seed
            for registration
            in Registration.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                status="CONFIRMADA",
            )
        }

        pairs = []

        for match in (
            self.get_first_round_matches()
        ):

            seed1 = (
                registrations.get(
                    match.player1_id
                )
                if match.player1_id
                else None
            )

            seed2 = (
                registrations.get(
                    match.player2_id
                )
                if match.player2_id
                else None
            )

            pairs.append(
                (
                    seed1,
                    seed2,
                )
            )

        return pairs

    # =====================================================
    # TAMAÑO DEL CUADRO
    # =====================================================

    def test_calculate_bracket_size_5_players(self):

        result = (
            BracketService
            ._calculate_bracket_size(
                5
            )
        )

        self.assertEqual(
            result,
            8
        )

    def test_calculate_bracket_size_8_players(self):

        result = (
            BracketService
            ._calculate_bracket_size(
                8
            )
        )

        self.assertEqual(
            result,
            8
        )

    def test_calculate_bracket_size_9_players(self):

        result = (
            BracketService
            ._calculate_bracket_size(
                9
            )
        )

        self.assertEqual(
            result,
            16
        )

    def test_calculate_bracket_size_16_players(self):

        result = (
            BracketService
            ._calculate_bracket_size(
                16
            )
        )

        self.assertEqual(
            result,
            16
        )

    def test_calculate_bracket_size_33_players(self):

        result = (
            BracketService
            ._calculate_bracket_size(
                33
            )
        )

        self.assertEqual(
            result,
            64
        )

    def test_calculate_bracket_size_64_players(self):

        result = (
            BracketService
            ._calculate_bracket_size(
                64
            )
        )

        self.assertEqual(
            result,
            64
        )

    # =====================================================
    # VALIDACIONES
    # =====================================================

    def test_cannot_generate_bracket_for_ladder(self):

        self.competition.type = (
            "ESCALERILLA"
        )

        self.competition.save()

        self.create_players(
            4
        )

        with self.assertRaises(
            ValidationError
        ):

            BracketService.generate_bracket(
                self.competition_category
            )

    def test_cannot_generate_without_minimum_players(self):

        self.competition_category.minimum_players = (
            4
        )

        self.competition_category.save()

        self.create_players(
            2
        )

        with self.assertRaises(
            ValidationError
        ):

            BracketService.generate_bracket(
                self.competition_category
            )

    def test_duplicate_seed_is_rejected(self):

        registrations = (
            self.create_players(
                4
            )
        )

        registrations[0].seed = 1
        registrations[0].save()

        registrations[1].seed = 1
        registrations[1].save()

        with self.assertRaises(
            ValidationError
        ):

            BracketService.generate_bracket(
                self.competition_category
            )

    def test_seed_greater_than_player_count_is_rejected(
        self
    ):

        registrations = (
            self.create_players(
                4
            )
        )

        registrations[0].seed = 8
        registrations[0].save()

        with self.assertRaises(
            ValidationError
        ):

            BracketService.generate_bracket(
                self.competition_category
            )

    def test_only_confirmed_registrations_are_used(self):

        registrations = (
            self.create_players(
                4
            )
        )

        registrations[3].status = (
            "PENDIENTE"
        )

        registrations[3].save()

        BracketService.generate_bracket(
            self.competition_category
        )

        player_ids_in_bracket = set()

        for match in (
            self.get_first_round_matches()
        ):

            if match.player1_id:

                player_ids_in_bracket.add(
                    match.player1_id
                )

            if match.player2_id:

                player_ids_in_bracket.add(
                    match.player2_id
                )

        self.assertNotIn(
            registrations[3].player_id,
            player_ids_in_bracket
        )

    # =====================================================
    # ESTRUCTURA 8 JUGADORES
    # =====================================================

    def test_generate_8_player_bracket_creates_7_matches(
        self
    ):

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        self.assertEqual(
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                )
            ).count(),
            7
        )

    def test_generate_8_player_bracket_creates_three_rounds(
        self
    ):

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        self.assertEqual(
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=1,
            ).count(),
            4
        )

        self.assertEqual(
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=2,
            ).count(),
            2
        )

        self.assertEqual(
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=3,
            ).count(),
            1
        )

    # =====================================================
    # TODOS CON SEED - 8
    # =====================================================

    def test_full_seeded_bracket_8_players_has_expected_pairs(
        self
    ):

        self.create_players(
            8,
            with_seeds=True,
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        pairs = (
            self.get_seed_pairs_from_first_round()
        )

        normalized_pairs = {
            frozenset(pair)
            for pair in pairs
        }

        expected = {
            frozenset((1, 8)),
            frozenset((2, 7)),
            frozenset((3, 6)),
            frozenset((4, 5)),
        }

        self.assertEqual(
            normalized_pairs,
            expected
        )

    def test_seed_1_and_2_are_in_opposite_halves_for_8(
        self
    ):

        self.create_players(
            8,
            with_seeds=True,
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        first_round = (
            self.get_first_round_matches()
        )

        registrations = {
            registration.player_id:
                registration.seed
            for registration
            in Registration.objects.filter(
                competition_category=(
                    self.competition_category
                )
            )
        }

        seed1_match_index = None
        seed2_match_index = None

        for index, match in enumerate(
            first_round
        ):

            seeds = {
                registrations.get(
                    match.player1_id
                ),
                registrations.get(
                    match.player2_id
                ),
            }

            if 1 in seeds:
                seed1_match_index = index

            if 2 in seeds:
                seed2_match_index = index

        self.assertIsNotNone(
            seed1_match_index
        )

        self.assertIsNotNone(
            seed2_match_index
        )

        self.assertLess(
            seed1_match_index,
            2
        )

        self.assertGreaterEqual(
            seed2_match_index,
            2
        )

    # =====================================================
    # TODOS CON SEED - 16
    # =====================================================

    def test_full_seeded_bracket_16_players_has_expected_pairs(
        self
    ):

        self.create_players(
            16,
            with_seeds=True,
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        pairs = (
            self.get_seed_pairs_from_first_round()
        )

        normalized_pairs = {
            frozenset(pair)
            for pair in pairs
        }

        expected = {
            frozenset((1, 16)),
            frozenset((2, 15)),
            frozenset((3, 14)),
            frozenset((4, 13)),
            frozenset((5, 12)),
            frozenset((6, 11)),
            frozenset((7, 10)),
            frozenset((8, 9)),
        }

        self.assertEqual(
            normalized_pairs,
            expected
        )

    def test_seed_1_and_2_are_in_opposite_halves_for_16(
        self
    ):

        self.create_players(
            16,
            with_seeds=True,
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        first_round = (
            self.get_first_round_matches()
        )

        seed_by_player = {
            registration.player_id:
                registration.seed
            for registration
            in Registration.objects.filter(
                competition_category=(
                    self.competition_category
                )
            )
        }

        seed1_index = None
        seed2_index = None

        for index, match in enumerate(
            first_round
        ):

            seeds = {
                seed_by_player.get(
                    match.player1_id
                ),
                seed_by_player.get(
                    match.player2_id
                ),
            }

            if 1 in seeds:
                seed1_index = index

            if 2 in seeds:
                seed2_index = index

        self.assertIsNotNone(
            seed1_index
        )

        self.assertIsNotNone(
            seed2_index
        )

        # 8 partidos:
        # primera mitad = índices 0..3
        # segunda mitad = índices 4..7

        self.assertLess(
            seed1_index,
            4
        )

        self.assertGreaterEqual(
            seed2_index,
            4
        )

    # =====================================================
    # TODOS CON SEED - 64
    # =====================================================

    def test_full_seeded_bracket_64_players_pairs_1_with_64(
        self
    ):

        self.competition_category.minimum_players = (
            2
        )

        self.competition_category.max_players = (
            64
        )

        self.competition_category.save()

        self.create_players(
            64,
            with_seeds=True,
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        pairs = (
            self.get_seed_pairs_from_first_round()
        )

        normalized_pairs = {
            frozenset(pair)
            for pair in pairs
        }

        self.assertIn(
            frozenset((1, 64)),
            normalized_pairs
        )

        self.assertIn(
            frozenset((2, 63)),
            normalized_pairs
        )

        self.assertIn(
            frozenset((32, 33)),
            normalized_pairs
        )

    def test_seed_1_and_2_are_in_opposite_halves_for_64(
        self
    ):

        self.competition_category.max_players = (
            64
        )

        self.competition_category.save()

        self.create_players(
            64,
            with_seeds=True,
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        first_round = (
            self.get_first_round_matches()
        )

        seed_by_player = {
            registration.player_id:
                registration.seed
            for registration
            in Registration.objects.filter(
                competition_category=(
                    self.competition_category
                )
            )
        }

        seed1_index = None
        seed2_index = None

        for index, match in enumerate(
            first_round
        ):

            seeds = {
                seed_by_player.get(
                    match.player1_id
                ),
                seed_by_player.get(
                    match.player2_id
                ),
            }

            if 1 in seeds:
                seed1_index = index

            if 2 in seeds:
                seed2_index = index

        self.assertIsNotNone(
            seed1_index
        )

        self.assertIsNotNone(
            seed2_index
        )

        # 32 partidos primera ronda.
        # Mitad superior: 0..15.
        # Mitad inferior: 16..31.

        self.assertLess(
            seed1_index,
            16
        )

        self.assertGreaterEqual(
            seed2_index,
            16
        )

    # =====================================================
    # ALGUNOS SEEDS
    # =====================================================

    def test_partial_seeding_does_not_match_seed_1_against_seed_2(
        self
    ):

        registrations = (
            self.create_players(
                8
            )
        )

        registrations[0].seed = 1
        registrations[0].save()

        registrations[1].seed = 2
        registrations[1].save()

        registrations[2].seed = 3
        registrations[2].save()

        registrations[3].seed = 4
        registrations[3].save()

        BracketService.generate_bracket(
            self.competition_category
        )

        pairs = (
            self.get_seed_pairs_from_first_round()
        )

        for pair in pairs:

            existing_seeds = [
                seed
                for seed in pair
                if seed is not None
            ]

            self.assertFalse(
                1 in existing_seeds
                and 2 in existing_seeds
            )

            self.assertFalse(
                3 in existing_seeds
                and 4 in existing_seeds
            )

    # =====================================================
    # BYE
    # =====================================================

    def test_6_players_generate_8_player_bracket_with_two_byes(
        self
    ):

        self.create_players(
            6
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        first_round = (
            self.get_first_round_matches()
        )

        bye_matches = [
            match
            for match in first_round
            if (
                (
                    match.player1 is None
                    and match.player2 is not None
                )
                or
                (
                    match.player1 is not None
                    and match.player2 is None
                )
            )
        ]

        self.assertEqual(
            len(bye_matches),
            2
        )

    def test_bye_match_is_finished_automatically(
        self
    ):

        self.create_players(
            6
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        first_round = (
            self.get_first_round_matches()
        )

        bye_matches = [
            match
            for match in first_round
            if (
                match.player1 is None
                or match.player2 is None
            )
            and (
                match.player1 is not None
                or match.player2 is not None
            )
        ]

        self.assertGreater(
            len(bye_matches),
            0
        )

        for match in bye_matches:

            self.assertEqual(
                match.status,
                Match.Status.FINALIZADO
            )

            self.assertIsNotNone(
                match.winner_player
            )

    def test_bye_winner_advances_to_next_round(
        self
    ):

        self.create_players(
            6
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        bye_match = next(
            match
            for match
            in self.get_first_round_matches()
            if (
                (
                    match.player1 is None
                    and match.player2 is not None
                )
                or
                (
                    match.player1 is not None
                    and match.player2 is None
                )
            )
        )

        bye_match.refresh_from_db()

        next_match = (
            bye_match.next_match
        )

        self.assertIsNotNone(
            next_match
        )

        next_match.refresh_from_db()

        if (
            bye_match.next_match_slot
            == 1
        ):

            self.assertEqual(
                next_match.player1,
                bye_match.winner_player
            )

        else:

            self.assertEqual(
                next_match.player2,
                bye_match.winner_player
            )

    # =====================================================
    # NEXT MATCH
    # =====================================================

    def test_first_round_matches_are_connected_to_second_round(
        self
    ):

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        first_round = (
            self.get_first_round_matches()
        )

        for match in first_round:

            self.assertIsNotNone(
                match.next_match
            )

            self.assertIn(
                match.next_match_slot,
                [
                    1,
                    2,
                ]
            )

            self.assertEqual(
                match.next_match.round,
                2
            )

    def test_final_has_no_next_match(
        self
    ):

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        final = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=3,
                bracket_position=1,
            )
        )

        self.assertIsNone(
            final.next_match
        )

        self.assertIsNone(
            final.next_match_slot
        )

    # =====================================================
    # REGENERACIÓN
    # =====================================================

    def test_bracket_cannot_be_generated_twice(
        self
    ):

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        with self.assertRaises(
            ValidationError
        ):

            BracketService.generate_bracket(
                self.competition_category
            )
        # =====================================================
    # AVANCE AUTOMÁTICO POR RESULTADO
    # =====================================================

    def _register_straight_sets_win(
        self,
        match,
        winner=1,
    ):
        """
        Registra un resultado 2-0 utilizando
        MatchSetSerializer.

        winner:
            1 -> gana player1
            2 -> gana player2
        """

        if winner == 1:

            set1 = {
                "match": match.id,
                "set_number": 1,
                "games_player1": 6,
                "games_player2": 3,
                "is_super_tie_break": False,
            }

            set2 = {
                "match": match.id,
                "set_number": 2,
                "games_player1": 6,
                "games_player2": 4,
                "is_super_tie_break": False,
            }

        else:

            set1 = {
                "match": match.id,
                "set_number": 1,
                "games_player1": 3,
                "games_player2": 6,
                "is_super_tie_break": False,
            }

            set2 = {
                "match": match.id,
                "set_number": 2,
                "games_player1": 4,
                "games_player2": 6,
                "is_super_tie_break": False,
            }

        serializer1 = MatchSetSerializer(
            data=set1
        )

        self.assertTrue(
            serializer1.is_valid(),
            serializer1.errors,
        )

        serializer1.save()

        serializer2 = MatchSetSerializer(
            data=set2
        )

        self.assertTrue(
            serializer2.is_valid(),
            serializer2.errors,
        )

        serializer2.save()

        match.refresh_from_db()

    def test_match_winner_advances_to_next_round(
        self
    ):
        """
        Ganador de cuartos debe aparecer
        automáticamente en semifinal.
        """

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        match = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=1,
                bracket_position=1,
            )
        )

        expected_winner = (
            match.player1
        )

        self._register_straight_sets_win(
            match,
            winner=1,
        )

        self.assertEqual(
            match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            match.winner_player,
            expected_winner,
        )

        next_match = (
            match.next_match
        )

        next_match.refresh_from_db()

        if match.next_match_slot == 1:

            self.assertEqual(
                next_match.player1,
                expected_winner,
            )

        else:

            self.assertEqual(
                next_match.player2,
                expected_winner,
            )

    def test_player2_can_advance_to_next_round(self):
        """
        El avance no depende de que gane player1.
        """

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        match = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=1,
                bracket_position=1,
            )
        )

        expected_winner = (
            match.player2
        )

        self.assertIsNotNone(
            expected_winner
        )



        self._register_straight_sets_win(
            match,
            winner=2,
        )

        match.refresh_from_db()



        next_match = (
            Match.objects.get(
                pk=match.next_match_id
            )
        )



        self.assertEqual(
            match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            match.winner_player,
            expected_winner,
        )

        if (
            match.next_match_slot == 1
        ):

            self.assertEqual(
                next_match.player1,
                expected_winner,
            )

        else:

            self.assertEqual(
                next_match.player2,
                expected_winner,
            )
    def test_semifinal_winner_advances_to_final(
        self
    ):
        """
        Se juegan dos cuartos que alimentan
        una semifinal.

        Después se juega esa semifinal y
        el ganador debe aparecer en la final.
        """

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        quarter1 = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=1,
                bracket_position=1,
            )
        )

        quarter2 = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=1,
                bracket_position=2,
            )
        )

        self._register_straight_sets_win(
            quarter1,
            winner=1,
        )

        self._register_straight_sets_win(
            quarter2,
            winner=1,
        )

        semifinal = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=2,
                bracket_position=1,
            )
        )

        semifinal.refresh_from_db()

        self.assertIsNotNone(
            semifinal.player1
        )

        self.assertIsNotNone(
            semifinal.player2
        )

        expected_winner = (
            semifinal.player1
        )

        self._register_straight_sets_win(
            semifinal,
            winner=1,
        )

        final = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=3,
                bracket_position=1,
            )
        )

        final.refresh_from_db()

        self.assertEqual(
            semifinal.winner_player,
            expected_winner,
        )

        if semifinal.next_match_slot == 1:

            self.assertEqual(
                final.player1,
                expected_winner,
            )

        else:

            self.assertEqual(
                final.player2,
                expected_winner,
            )

    def test_complete_8_player_bracket_produces_champion(
        self
    ):
        """
        Simula un cuadro completo de 8 jugadores:

        4 cuartos
        2 semifinales
        1 final

        El ganador de la final queda campeón
        y no tiene partido siguiente.
        """

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        # ---------------------------------
        # CUARTOS
        # ---------------------------------

        quarterfinals = list(
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=1,
            ).order_by(
                "bracket_position"
            )
        )

        self.assertEqual(
            len(quarterfinals),
            4,
        )

        for match in quarterfinals:

            self._register_straight_sets_win(
                match,
                winner=1,
            )

        # ---------------------------------
        # SEMIFINALES
        # ---------------------------------

        semifinals = list(
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=2,
            ).order_by(
                "bracket_position"
            )
        )

        self.assertEqual(
            len(semifinals),
            2,
        )

        for semifinal in semifinals:

            semifinal.refresh_from_db()

            self.assertIsNotNone(
                semifinal.player1
            )

            self.assertIsNotNone(
                semifinal.player2
            )

            self._register_straight_sets_win(
                semifinal,
                winner=1,
            )

        # ---------------------------------
        # FINAL
        # ---------------------------------

        final = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=3,
                bracket_position=1,
            )
        )

        final.refresh_from_db()

        self.assertIsNotNone(
            final.player1
        )

        self.assertIsNotNone(
            final.player2
        )

        expected_champion = (
            final.player1
        )

        self._register_straight_sets_win(
            final,
            winner=1,
        )

        final.refresh_from_db()

        # ---------------------------------
        # CAMPEÓN
        # ---------------------------------

        self.assertEqual(
            final.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            final.winner_player,
            expected_champion,
        )

        self.assertIsNone(
            final.next_match
        )

        self.assertIsNone(
            final.next_match_slot
        )

    def test_final_winner_does_not_create_extra_match(
        self
    ):
        """
        Ganar la final no debe crear otra ronda
        ni otro partido.
        """

        self.create_players(
            8
        )

        BracketService.generate_bracket(
            self.competition_category
        )

        initial_match_count = (
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                )
            ).count()
        )

        self.assertEqual(
            initial_match_count,
            7,
        )

        # Cuartos
        for match in (
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=1,
            ).order_by(
                "bracket_position"
            )
        ):

            self._register_straight_sets_win(
                match,
                winner=1,
            )

        # Semifinales
        for match in (
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                ),
                round=2,
            ).order_by(
                "bracket_position"
            )
        ):

            match.refresh_from_db()

            self._register_straight_sets_win(
                match,
                winner=1,
            )

        final = (
            Match.objects.get(
                competition_category=(
                    self.competition_category
                ),
                round=3,
                bracket_position=1,
            )
        )

        final.refresh_from_db()

        self._register_straight_sets_win(
            final,
            winner=1,
        )

        final_match_count = (
            Match.objects.filter(
                competition_category=(
                    self.competition_category
                )
            ).count()
        )

        self.assertEqual(
            final_match_count,
            7,
        )
        
class MatchResolutionAPITest(TestCase):

    def setUp(self):

        self.client = APIClient()

        # =================================================
        # ROLES
        # =================================================

        self.admin_role = Role.objects.create(
            name="Administrador"
        )

        self.player_role = Role.objects.create(
            name="Jugador"
        )

        User = get_user_model()

        # =================================================
        # ADMIN
        # =================================================

        self.admin_user = User.objects.create_user(
            username="resolution_admin",
            password="TestPassword123!",
            email="resolution_admin@tenis.cl",
            role=self.admin_role,
        )

        # =================================================
        # CATEGORÍA
        # =================================================

        self.category = Category.objects.create(
            name="RESOLUTION_CATEGORY"
        )

        # =================================================
        # JUGADORES
        # =================================================

        self.player1_user = User.objects.create_user(
            username="resolution_player1",
            password="TestPassword123!",
            email="resolution_player1@tenis.cl",
            role=self.player_role,
        )

        self.player2_user = User.objects.create_user(
            username="resolution_player2",
            password="TestPassword123!",
            email="resolution_player2@tenis.cl",
            role=self.player_role,
        )

        self.player3_user = User.objects.create_user(
            username="resolution_player3",
            password="TestPassword123!",
            email="resolution_player3@tenis.cl",
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

        self.player3 = Player.objects.create(
            user=self.player3_user,
            category=self.category,
            rut="53333333-3",
            first_name="Jugador",
            last_name="Tres",
        )

        # =================================================
        # COMPETENCIA ELIMINACIÓN DIRECTA
        # =================================================

        self.competition = Competition.objects.create(
            name="Torneo Resoluciones",
            type="ELIMINACION_DIRECTA",
            start_date="2026-09-01",
            end_date="2026-09-15",
            registration_deadline="2026-08-28",
        )

        self.competition_category = (
            CompetitionCategory.objects.create(
                competition=self.competition,
                category=self.category,
                max_players=16,
                minimum_players=2,
            )
        )

        # =================================================
        # INSCRIPCIONES
        # =================================================

        for player in [
            self.player1,
            self.player2,
            self.player3,
        ]:

            Registration.objects.create(
                competition_category=(
                    self.competition_category
                ),
                player=player,
                status="CONFIRMADA",
            )

        # =================================================
        # PARTIDO BASE
        # =================================================

        self.match = Match.objects.create(
            competition_category=(
                self.competition_category
            ),
            player1=self.player1,
            player2=self.player2,
            round=1,
            bracket_position=1,
            status=(
                Match.Status.PROGRAMADO
            ),
        )

    # =====================================================
    # AUTH
    # =====================================================

    def authenticate(
        self,
        user
    ):

        response = self.client.post(
            "/api/token/",
            {
                "username": user.username,
                "password": (
                    "TestPassword123!"
                ),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer "
                f"{response.data['access']}"
            )
        )

    # =====================================================
    # HELPER CREAR SET POR API
    # =====================================================

    def create_set_via_api(
        self,
        *,
        set_number,
        games_player1,
        games_player2,
        is_super_tie_break=False,
        is_incomplete=False,
    ):

        return self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    set_number,

                "games_player1":
                    games_player1,

                "games_player2":
                    games_player2,

                "is_super_tie_break":
                    is_super_tie_break,

                "is_incomplete":
                    is_incomplete,
            },
            format="json",
        )

    # =====================================================
    # WALKOVER
    # =====================================================

    def test_walkover_without_sets_is_allowed(
        self
    ):
        """
        Un partido sin sets puede terminar
        por walkover.
        """

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/walkover/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            self.match.winner_player,
            self.player1,
        )

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.WALKOVER,
        )

        self.assertTrue(
            self.match.is_walkover
        )

    def test_walkover_with_existing_sets_is_rejected(
        self
    ):
        """
        Si ya existe juego registrado,
        no corresponde WO sino Retiro.
        """

        MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
            is_super_tie_break=False,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/walkover/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.NORMAL,
        )

    def test_walkover_requires_winner(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/walkover/"
            ),
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "winner_player",
            response.data,
        )

    def test_walkover_winner_must_be_match_player(
        self
    ):

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/walkover/"
            ),
            {
                "winner_player":
                    self.player3.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================================
    # RETIRO
    # =====================================================

    def test_retirement_without_sets_is_allowed(
        self
    ):
        """
        El retiro puede ocurrir al comienzo
        del partido aunque todavía no exista
        ningún set registrado.
        """

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/retirement/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            self.match.winner_player,
            self.player1,
        )

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.RETIREMENT,
        )

        self.assertFalse(
            self.match.is_walkover
        )

        self.assertFalse(
            self.match.sets.exists()
        )

    def test_retirement_with_existing_set_is_allowed(
        self
    ):
        """
        El retiro conserva lo jugado
        y finaliza el partido.
        """

        match_set = MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
            is_super_tie_break=False,
        )

        self.match.status = (
            Match.Status.EN_JUEGO
        )

        self.match.save(
            update_fields=[
                "status",
            ]
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/retirement/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            self.match.winner_player,
            self.player1,
        )

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.RETIREMENT,
        )

        self.assertFalse(
            self.match.is_walkover
        )

        self.assertTrue(
            MatchSet.objects.filter(
                pk=match_set.id
            ).exists()
        )

    def test_retirement_winner_must_be_match_player(
        self
    ):

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
            (
                f"/api/matches/"
                f"{self.match.id}/retirement/"
            ),
            {
                "winner_player":
                    self.player3.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # =====================================================
    # SETS INCOMPLETOS
    # =====================================================

    def test_incomplete_first_set_is_allowed(
        self
    ):
        """
        Un marcador parcial como 5-2
        debe poder registrarse.
        """

        self.authenticate(
            self.admin_user
        )

        response = self.create_set_via_api(
            set_number=1,
            games_player1=5,
            games_player2=2,
            is_incomplete=True,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        match_set = MatchSet.objects.get(
            match=self.match,
            set_number=1,
        )

        self.assertTrue(
            match_set.is_incomplete
        )

        self.assertEqual(
            match_set.games_player1,
            5,
        )

        self.assertEqual(
            match_set.games_player2,
            2,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            Match.Status.EN_JUEGO,
        )

        self.assertIsNone(
            self.match.winner_player
        )

    def test_incomplete_set_does_not_count_as_set_win(
        self
    ):
        """
        Un set incompleto no puede otorgar
        un set ganado.
        """

        self.authenticate(
            self.admin_user
        )

        response = self.create_set_via_api(
            set_number=1,
            games_player1=5,
            games_player2=2,
            is_incomplete=True,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            Match.Status.EN_JUEGO,
        )

        self.assertIsNone(
            self.match.winner_player
        )

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.NORMAL,
        )

    def test_completed_score_cannot_be_marked_incomplete(
        self
    ):
        """
        Un marcador que ya constituye
        un set terminado, como 6-2,
        no puede marcarse incompleto.
        """

        self.authenticate(
            self.admin_user
        )

        response = self.create_set_via_api(
            set_number=1,
            games_player1=6,
            games_player2=2,
            is_incomplete=True,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            MatchSet.objects.filter(
                match=self.match,
                set_number=1,
            ).exists()
        )

    def test_cannot_create_later_set_after_incomplete_set(
        self
    ):
        """
        Un set incompleto siempre debe
        ser el último set registrado.
        """

        self.authenticate(
            self.admin_user
        )

        response1 = self.create_set_via_api(
            set_number=1,
            games_player1=5,
            games_player2=2,
            is_incomplete=True,
        )

        self.assertEqual(
            response1.status_code,
            status.HTTP_201_CREATED,
        )

        response2 = self.create_set_via_api(
            set_number=2,
            games_player1=6,
            games_player2=4,
        )

        self.assertEqual(
            response2.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            MatchSet.objects.filter(
                match=self.match,
                set_number=2,
            ).exists()
        )

    # =====================================================
    # RETIRO CON MARCADOR PARCIAL
    # =====================================================

    def test_retirement_with_incomplete_first_set_preserves_score(
        self
    ):
        """
        Caso:
        5-2 RET.
        """

        self.authenticate(
            self.admin_user
        )

        set_response = self.create_set_via_api(
            set_number=1,
            games_player1=5,
            games_player2=2,
            is_incomplete=True,
        )

        self.assertEqual(
            set_response.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/retirement/"
            ),
            {
                "winner_player":
                    self.player2.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.match.refresh_from_db()

        partial_set = MatchSet.objects.get(
            match=self.match,
            set_number=1,
        )

        self.assertTrue(
            partial_set.is_incomplete
        )

        self.assertEqual(
            partial_set.games_player1,
            5,
        )

        self.assertEqual(
            partial_set.games_player2,
            2,
        )

        self.assertEqual(
            self.match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            self.match.winner_player,
            self.player2,
        )

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.RETIREMENT,
        )

    def test_retirement_during_second_set_preserves_scores(
        self
    ):
        """
        Caso:
        6-4, 2-1 RET.
        """

        self.authenticate(
            self.admin_user
        )

        response1 = self.create_set_via_api(
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.assertEqual(
            response1.status_code,
            status.HTTP_201_CREATED,
        )

        response2 = self.create_set_via_api(
            set_number=2,
            games_player1=2,
            games_player2=1,
            is_incomplete=True,
        )

        self.assertEqual(
            response2.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/retirement/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        sets = list(
            MatchSet.objects
            .filter(
                match=self.match
            )
            .order_by(
                "set_number"
            )
        )

        self.assertEqual(
            len(sets),
            2,
        )

        self.assertFalse(
            sets[0].is_incomplete
        )

        self.assertTrue(
            sets[1].is_incomplete
        )

        self.assertEqual(
            sets[1].games_player1,
            2,
        )

        self.assertEqual(
            sets[1].games_player2,
            1,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.RETIREMENT,
        )

    def test_retirement_during_super_tie_break_is_allowed(
        self
    ):
        """
        Caso:
        6-4, 4-6, 5-3 RET.
        """

        self.authenticate(
            self.admin_user
        )

        response1 = self.create_set_via_api(
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.assertEqual(
            response1.status_code,
            status.HTTP_201_CREATED,
        )

        response2 = self.create_set_via_api(
            set_number=2,
            games_player1=4,
            games_player2=6,
        )

        self.assertEqual(
            response2.status_code,
            status.HTTP_201_CREATED,
        )

        response3 = self.create_set_via_api(
            set_number=3,
            games_player1=5,
            games_player2=3,
            is_super_tie_break=True,
            is_incomplete=True,
        )

        self.assertEqual(
            response3.status_code,
            status.HTTP_201_CREATED,
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/retirement/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        stb = MatchSet.objects.get(
            match=self.match,
            set_number=3,
        )

        self.assertTrue(
            stb.is_super_tie_break
        )

        self.assertTrue(
            stb.is_incomplete
        )

        self.assertEqual(
            stb.games_player1,
            5,
        )

        self.assertEqual(
            stb.games_player2,
            3,
        )

        self.match.refresh_from_db()

        self.assertEqual(
            self.match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.RETIREMENT,
        )

    # =====================================================
    # AVANCE EN ELIMINACIÓN DIRECTA
    # =====================================================

    def test_walkover_winner_advances_in_direct_elimination(
        self
    ):

        next_match = Match.objects.create(
            competition_category=(
                self.competition_category
            ),
            player1=None,
            player2=None,
            round=2,
            bracket_position=1,
            status=(
                Match.Status.PROGRAMADO
            ),
        )

        self.match.next_match = (
            next_match
        )

        self.match.next_match_slot = 1

        self.match.save(
            update_fields=[
                "next_match",
                "next_match_slot",
            ]
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/walkover/"
            ),
            {
                "winner_player":
                    self.player2.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        next_match.refresh_from_db()

        self.assertEqual(
            next_match.player1,
            self.player2,
        )

    def test_retirement_winner_advances_in_direct_elimination(
        self
    ):

        next_match = Match.objects.create(
            competition_category=(
                self.competition_category
            ),
            player1=None,
            player2=None,
            round=2,
            bracket_position=1,
        )

        self.match.next_match = (
            next_match
        )

        self.match.next_match_slot = 2

        self.match.status = (
            Match.Status.EN_JUEGO
        )

        self.match.save(
            update_fields=[
                "next_match",
                "next_match_slot",
                "status",
            ]
        )

        MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=4,
            games_player2=6,
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{self.match.id}/retirement/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        next_match.refresh_from_db()

        self.assertEqual(
            next_match.player2,
            self.player1,
        )

    # =====================================================
    # ESCALERILLA
    # =====================================================

    def test_walkover_does_not_propagate_bracket_in_ladder(
        self
    ):

        ladder_competition = (
            Competition.objects.create(
                name="Escalerilla Resolución",
                type="ESCALERILLA",
                start_date="2026-09-01",
                end_date="2026-09-30",
                registration_deadline="2026-08-28",
            )
        )

        ladder_category = (
            CompetitionCategory.objects.create(
                competition=(
                    ladder_competition
                ),
                category=self.category,
                max_players=16,
                minimum_players=2,
            )
        )

        for player in [
            self.player1,
            self.player2,
        ]:

            Registration.objects.create(
                competition_category=(
                    ladder_category
                ),
                player=player,
                status="CONFIRMADA",
            )

        fake_next_match = (
            Match.objects.create(
                competition_category=(
                    ladder_category
                ),
                player1=None,
                player2=None,
                round=None,
            )
        )

        ladder_match = (
            Match.objects.create(
                competition_category=(
                    ladder_category
                ),
                player1=self.player1,
                player2=self.player2,
                round=None,
                next_match=(
                    fake_next_match
                ),
                next_match_slot=1,
            )
        )

        self.authenticate(
            self.admin_user
        )

        response = self.client.post(
            (
                f"/api/matches/"
                f"{ladder_match.id}/walkover/"
            ),
            {
                "winner_player":
                    self.player1.id,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        ladder_match.refresh_from_db()
        fake_next_match.refresh_from_db()

        self.assertEqual(
            ladder_match.status,
            Match.Status.FINALIZADO,
        )

        self.assertEqual(
            ladder_match.winner_player,
            self.player1,
        )

        self.assertEqual(
            ladder_match.resolution_type,
            Match.ResolutionType.WALKOVER,
        )

        self.assertIsNone(
            fake_next_match.player1
        )

        self.assertIsNone(
            fake_next_match.player2
        )

    # =====================================================
    # RESET RETIRO
    # =====================================================

    def test_reset_retirement_preserves_incomplete_set(
        self
    ):
        """
        Un 5-2 RET restablecido a NORMAL
        conserva el parcial y vuelve EN_JUEGO.
        """

        self.authenticate(
            self.admin_user
        )

        response = self.create_set_via_api(
            set_number=1,
            games_player1=5,
            games_player2=2,
            is_incomplete=True,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        retirement_response = (
            self.client.post(
                (
                    f"/api/matches/"
                    f"{self.match.id}/retirement/"
                ),
                {
                    "winner_player":
                        self.player2.id,
                },
                format="json",
            )
        )

        self.assertEqual(
            retirement_response.status_code,
            status.HTTP_200_OK,
        )

        reset_response = (
            self.client.post(
                (
                    f"/api/matches/"
                    f"{self.match.id}/reset-resolution/"
                ),
                {},
                format="json",
            )
        )

        self.assertEqual(
            reset_response.status_code,
            status.HTTP_200_OK,
        )

        self.match.refresh_from_db()

        partial_set = MatchSet.objects.get(
            match=self.match,
            set_number=1,
        )

        self.assertEqual(
            self.match.resolution_type,
            Match.ResolutionType.NORMAL,
        )

        self.assertFalse(
            self.match.is_walkover
        )

        self.assertEqual(
            self.match.status,
            Match.Status.EN_JUEGO,
        )

        self.assertIsNone(
            self.match.winner_player
        )

        self.assertTrue(
            partial_set.is_incomplete
        )

        self.assertEqual(
            partial_set.games_player1,
            5,
        )

        self.assertEqual(
            partial_set.games_player2,
            2,
        )

    # =====================================================
    # BLOQUEAR SETS DESPUÉS DE RETIRO
    # =====================================================

    def test_cannot_add_sets_after_retirement(
        self
    ):

        MatchSet.objects.create(
            match=self.match,
            set_number=1,
            games_player1=6,
            games_player2=4,
        )

        self.match.status = (
            Match.Status.EN_JUEGO
        )

        self.match.save(
            update_fields=[
                "status",
            ]
        )

        self.authenticate(
            self.admin_user
        )

        retirement_response = (
            self.client.post(
                (
                    f"/api/matches/"
                    f"{self.match.id}/retirement/"
                ),
                {
                    "winner_player":
                        self.player1.id,
                },
                format="json",
            )
        )

        self.assertEqual(
            retirement_response.status_code,
            status.HTTP_200_OK,
        )

        response = self.client.post(
            "/api/match-sets/",
            {
                "match":
                    self.match.id,

                "set_number":
                    2,

                "games_player1":
                    6,

                "games_player2":
                    3,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
