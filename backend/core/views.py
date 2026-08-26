from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

# from rest_framework.permissions import IsAuthenticated
from core.utils import create_audit_log
from .models import (
    Category,
    Competition,
    CompetitionCategory,
    Player,
    Registration,
    Court,
    Match,
    MatchSet,
    Standing
)
from .permissions import PlayerPermission, CompetitionPermission
from .serializers import (
    CategorySerializer,
    CompetitionSerializer,
    CompetitionCategorySerializer,
    PlayerSerializer,
    RegistrationSerializer,
    CourtSerializer,
    MatchSerializer,
    MatchSetSerializer,
    StandingSerializer
)
from .permissions import (
    PlayerPermission,
    CompetitionPermission,
    RegistrationPermission,
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




class AuditModelViewSet(viewsets.ModelViewSet):

    def perform_create(self, serializer):
        instance = serializer.save()

        create_audit_log(
            user=self.request.user,
            action="CREATE",
            instance=instance,
        )

    def perform_update(self, serializer):
        instance = serializer.save()

        create_audit_log(
            user=self.request.user,
            action="UPDATE",
            instance=instance,
        )

    def perform_destroy(self, instance):
        # Guardamos los datos necesarios antes de eliminarlo
        create_audit_log(
            user=self.request.user,
            action="DELETE",
            instance=instance,
        )

        instance.delete()


class PlayerViewSet(AuditModelViewSet):
    """
    API para la gestión de jugadores.
    """

    queryset = Player.objects.select_related("user").all()
    serializer_class = PlayerSerializer
    permission_classes = [PlayerPermission]
    

class CompetitionViewSet(AuditModelViewSet):
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
    
class CompetitionCategoryViewSet(AuditModelViewSet):
    """
    API para configurar las categorías de una competencia.
    """

    queryset = CompetitionCategory.objects.select_related(
        "competition",
        "category",
    ).all()

    serializer_class = CompetitionCategorySerializer
    permission_classes = [
    RegistrationPermission
]

class RegistrationViewSet(AuditModelViewSet):
    """
    API para la gestión de inscripciones.
    """

    queryset = Registration.objects.select_related(
        "player",
        "player__category",
        "competition_category",
        "competition_category__competition",
        "competition_category__category",
    ).all()

    serializer_class = RegistrationSerializer
    permission_classes = [CompetitionPermission]
    
    
class CourtViewSet(AuditModelViewSet):

    queryset = Court.objects.all().order_by("name")
    serializer_class = CourtSerializer
    permission_classes = [CompetitionPermission]
    
    
class MatchViewSet(AuditModelViewSet):

    queryset = Match.objects.select_related(
        "competition_category",
        "competition_category__competition",
        "competition_category__category",
        "court",
        "player1",
        "player2",
        "winner_player",
    ).all()

    serializer_class = MatchSerializer
    permission_classes = [CompetitionPermission]
    
    
class MatchSetViewSet(AuditModelViewSet):

    queryset = MatchSet.objects.select_related(
        "match",
        "match__competition_category",
        "match__player1",
        "match__player2",
    ).all()

    serializer_class = MatchSetSerializer
    permission_classes = [CompetitionPermission]
    
class StandingViewSet(AuditModelViewSet):

    queryset = Standing.objects.select_related(
        "competition_category",
        "competition_category__competition",
        "competition_category__category",
        "player",
    ).all()

    serializer_class = StandingSerializer
    permission_classes = [CompetitionPermission]
    
    
    