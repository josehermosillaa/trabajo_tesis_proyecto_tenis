from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

# from rest_framework.permissions import IsAuthenticated

from .models import (
    Category,
    Competition,
    CompetitionCategory,
    Player,
)
from .permissions import PlayerPermission, CompetitionPermission
from .serializers import (
    CategorySerializer,
    CompetitionCategorySerializer,
    CompetitionSerializer,
    PlayerSerializer,
)

class HealthAPIView(APIView):

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(
            {
                "status": "OK",
                "application": "Sistema de Gestión de Torneos de Tenis",
                "version": "1.0.0",
            },
            status=status.HTTP_200_OK,
        )
        


class PlayerViewSet(viewsets.ModelViewSet):
    """
    API para la gestión de jugadores.
    """

    queryset = Player.objects.select_related("user").all()
    serializer_class = PlayerSerializer
    permission_classes = [PlayerPermission]
    

class CompetitionViewSet(viewsets.ModelViewSet):
    """
    API para la gestión de competencias.
    """

    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [CompetitionPermission]
    
class CategoryViewSet(viewsets.ModelViewSet):
    """
    API para la gestión de categorías.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CompetitionPermission]
    
class CompetitionCategoryViewSet(viewsets.ModelViewSet):
    """
    API para configurar las categorías de una competencia.
    """

    queryset = CompetitionCategory.objects.select_related(
        "competition",
        "category",
    ).all()

    serializer_class = CompetitionCategorySerializer
    permission_classes = [CompetitionPermission]