from rest_framework.permissions import BasePermission


class PlayerPermission(BasePermission):
    """
    Permisos para la gestión de jugadores según el rol del usuario.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = request.user.role.name

        # Lectura: todos los roles autenticados
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Creación: Administrador y Organizador
        if request.method == "POST":
            return role in ["Administrador", "Organizador"]

        # Modificación: Administrador y Organizador
        if request.method in ["PUT", "PATCH"]:
            return role in ["Administrador", "Organizador"]

        # Eliminación: solamente Administrador
        if request.method == "DELETE":
            return role == "Administrador"

        return False
    
class CompetitionPermission(BasePermission):
    """
    Permisos para la gestión de competencias según el rol del usuario.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role = request.user.role.name

        # Consulta: todos los usuarios autenticados
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True

        # Crear: Administrador y Organizador
        if request.method == "POST":
            return role in ["Administrador", "Organizador"]

        # Modificar: Administrador y Organizador
        if request.method in ["PUT", "PATCH"]:
            return role in ["Administrador", "Organizador"]

        # Eliminar: solamente Administrador
        if request.method == "DELETE":
            return role == "Administrador"

        return False


class MatchSetPermission(CompetitionPermission):
    """Permite la gestión operativa de sets a Administrador y Organizador."""

    def has_permission(self, request, view):
        if request.method == "DELETE":
            return bool(
                request.user
                and request.user.is_authenticated
                and request.user.role_id
                and request.user.role.name in ["Administrador", "Organizador"]
            )

        return super().has_permission(request, view)


class CompetitionCategoryPermission(CompetitionPermission):
    """Permite eliminar categorías a Administrador y Organizador."""

    def has_permission(self, request, view):
        if request.method == "DELETE":
            return bool(
                request.user
                and request.user.is_authenticated
                and request.user.role_id
                and request.user.role.name in ["Administrador", "Organizador"]
            )

        return super().has_permission(request, view)
    
class RegistrationPermission(BasePermission):

    def has_permission(
        self,
        request,
        view
    ):

        if (
            not request.user
            or not request.user.is_authenticated
        ):
            return False

        role = request.user.role.name

        if request.method in [
            "GET",
            "HEAD",
            "OPTIONS",
        ]:
            return True

        if request.method == "POST":
            return role in [
                "Administrador",
                "Organizador",
                "Jugador",
            ]

        if request.method in [
            "PUT",
            "PATCH",
        ]:
            return role in [
                "Administrador",
                "Organizador",
            ]

        if request.method == "DELETE":
            return (
                role == "Administrador"
            )

        return False
    """
    Permisos para la gestión de inscripciones.
    """

    def has_permission(self, request, view):

        if (
            not request.user
            or not request.user.is_authenticated
        ):
            return False

        role = request.user.role.name

        # Todos los usuarios autenticados
        # pueden consultar inscripciones.
        if request.method in [
            "GET",
            "HEAD",
            "OPTIONS",
        ]:
            return True

        # Crear:
        # Admin y Organizador inscriben jugadores.
        # Jugador puede inscribirse a sí mismo.
        if request.method == "POST":
            return role in [
                "Administrador",
                "Organizador",
                "Jugador",
            ]

        # Editar:
        # solamente Admin y Organizador.
        if request.method in [
            "PUT",
            "PATCH",
        ]:
            return role in [
                "Administrador",
                "Organizador",
            ]

        # Eliminar:
        # solamente Administrador.
        if request.method == "DELETE":
            return role == "Administrador"

        return False
