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