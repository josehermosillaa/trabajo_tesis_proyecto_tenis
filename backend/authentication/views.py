from rest_framework_simplejwt.views import (
    TokenObtainPairView,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    RoleTokenObtainPairSerializer,
    OrganizerActiveSerializer,
    OrganizerSerializer,
)
from .models import User
from .permissions import IsAdministrator


class RoleTokenObtainPairView(
    TokenObtainPairView
):
    serializer_class = (
        RoleTokenObtainPairSerializer
    )


class OrganizerViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizerSerializer
    permission_classes = [IsAdministrator]
    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_queryset(self):
        return (
            User.objects.filter(role__name="Organizador")
            .select_related("role")
            .order_by("last_name", "first_name", "username", "id")
        )

    @action(detail=True, methods=["post"], url_path="set-active")
    def set_active(self, request, pk=None):
        organizer = self.get_object()
        serializer = OrganizerActiveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        organizer.is_active = serializer.validated_data["active"]
        organizer.save(update_fields=["is_active"])
        return Response(
            OrganizerSerializer(organizer).data,
            status=status.HTTP_200_OK,
        )
