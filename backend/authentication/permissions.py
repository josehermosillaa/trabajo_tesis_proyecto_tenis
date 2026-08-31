from rest_framework.permissions import BasePermission


class IsAdministrator(BasePermission):
    message = "Solo un administrador puede gestionar organizadores."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role_id
            and request.user.role.name == "Administrador"
        )
