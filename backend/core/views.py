from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
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
from .services.bracket_service import (
    BracketService,
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
    
class CompetitionCategoryViewSet(
    AuditModelViewSet
):

    queryset = (
        CompetitionCategory.objects
        .select_related(
            "competition",
            "category",
        )
        .all()
    )

    serializer_class = (
        CompetitionCategorySerializer
    )

    permission_classes = [
        CompetitionPermission
    ]

    # =====================================================
    # ELIMINAR CATEGORÍA
    # =====================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        instance = (
            self.get_object()
        )

        has_active_registrations = (
            instance.registrations
            .exclude(
                status="CANCELADA"
            )
            .exists()
        )

        if has_active_registrations:

            return Response(
                {
                    "detail": (
                        "No se puede eliminar la categoría "
                        "porque tiene jugadores inscritos."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return super().destroy(
            request,
            *args,
            **kwargs,
        )

    # =====================================================
    # GENERAR CUADRO
    # =====================================================

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="generate-bracket",
    )
    def generate_bracket(
        self,
        request,
        pk=None,
    ):
        """
        Genera automáticamente el cuadro
        de eliminación directa.

        Solo usa inscripciones CONFIRMADAS.

        BracketService valida:

        - tipo ELIMINACION_DIRECTA
        - mínimo de jugadores
        - máximo de jugadores
        - seeds
        - cuadro previamente generado
        """

        competition_category = (
            self.get_object()
        )

        BracketService.generate_bracket(
            competition_category
        )

        matches = (
            Match.objects
            .filter(
                competition_category=(
                    competition_category
                )
            )
            .select_related(
                "competition_category",
                "player1",
                "player2",
                "winner_player",
                "court",
                "next_match",
            )
            .prefetch_related(
                "sets"
            )
            .order_by(
                "round",
                "bracket_position",
            )
        )

        serializer = (
            MatchSerializer(
                matches,
                many=True,
            )
        )

        return Response(
            {
                "detail": (
                    "Cuadro generado correctamente."
                ),
                "competition_category": (
                    competition_category.id
                ),
                "matches": (
                    serializer.data
                ),
            },
            status=(
                status.HTTP_201_CREATED
            ),
        )

    # =====================================================
    # CONSULTAR CUADRO
    # =====================================================

    @action(
        detail=True,
        methods=[
            "get",
        ],
        url_path="bracket",
    )
    def bracket(
        self,
        request,
        pk=None,
    ):
        """
        Devuelve el cuadro completo ordenado
        por ronda y posición.
        """

        competition_category = (
            self.get_object()
        )

        if (
            competition_category
            .competition
            .type
            != "ELIMINACION_DIRECTA"
        ):

            return Response(
                {
                    "detail": (
                        "Esta categoría pertenece a una "
                        "competencia que no utiliza cuadro "
                        "de eliminación directa."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        matches = (
            Match.objects
            .filter(
                competition_category=(
                    competition_category
                )
            )
            .select_related(
                "competition_category",
                "player1",
                "player2",
                "winner_player",
                "court",
                "next_match",
            )
            .prefetch_related(
                "sets"
            )
            .order_by(
                "round",
                "bracket_position",
            )
        )

        serializer = (
            MatchSerializer(
                matches,
                many=True,
            )
        )

        return Response(
            {
                "competition_category": (
                    competition_category.id
                ),
                "competition": (
                    competition_category
                    .competition
                    .id
                ),
                "competition_name": (
                    competition_category
                    .competition
                    .name
                ),
                "category": (
                    competition_category
                    .category
                    .id
                ),
                "category_name": (
                    competition_category
                    .category
                    .name
                ),
                "generated": (
                    matches.exists()
                ),
                "matches": (
                    serializer.data
                ),
            },
            status=(
                status.HTTP_200_OK
            ),
        )
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

    permission_classes = [
        RegistrationPermission
    ]
    
class CourtViewSet(AuditModelViewSet):

    queryset = Court.objects.all().order_by("name")
    serializer_class = CourtSerializer
    permission_classes = [CompetitionPermission]
    
    
class MatchViewSet(
    AuditModelViewSet
):

    queryset = (
        Match.objects
        .select_related(
            "competition_category",
            "competition_category__competition",
            "competition_category__category",
            "court",
            "player1",
            "player2",
            "winner_player",
            "next_match",
        )
        .prefetch_related(
            "sets"
        )
        .all()
    )

    serializer_class = (
        MatchSerializer
    )

    permission_classes = [
        CompetitionPermission
    ]

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def _get_winner_from_request(
        request,
        match,
    ):
        """
        Obtiene y valida el ganador enviado
        desde el frontend.
        """

        winner_id = (
            request.data.get(
                "winner_player"
            )
        )

        if winner_id is None:

            return (
                None,
                Response(
                    {
                        "winner_player": (
                            "Debe indicar el jugador "
                            "ganador."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )
            )

        try:

            winner_id = int(
                winner_id
            )

        except (
            TypeError,
            ValueError,
        ):

            return (
                None,
                Response(
                    {
                        "winner_player": (
                            "El jugador ganador "
                            "no es válido."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )
            )

        valid_player_ids = [
            player_id
            for player_id in [
                match.player1_id,
                match.player2_id,
            ]
            if player_id is not None
        ]

        if (
            winner_id
            not in valid_player_ids
        ):

            return (
                None,
                Response(
                    {
                        "winner_player": (
                            "El ganador debe ser uno "
                            "de los jugadores del partido."
                        )
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )
            )

        winner = (
            match.player1
            if (
                match.player1_id
                == winner_id
            )
            else match.player2
        )

        return (
            winner,
            None,
        )

    # =====================================================
    # WALKOVER
    # =====================================================

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="walkover",
    )
    def walkover(
        self,
        request,
        pk=None,
    ):
        """
        Finaliza un partido por WALKOVER.

        Reglas:

        - deben existir dos jugadores;
        - no debe existir ningún set;
        - debe indicarse ganador;
        - finaliza inmediatamente;
        - en eliminación directa avanza al ganador.
        """

        match = (
            self.get_object()
        )

        # ---------------------------------
        # Proteger rondas posteriores
        # ---------------------------------

        MatchSetSerializer.ensure_result_is_editable(
            match
        )

        # ---------------------------------
        # Jugadores definidos
        # ---------------------------------

        if (
            match.player1_id is None
            or match.player2_id is None
        ):

            return Response(
                {
                    "detail": (
                        "No se puede registrar un "
                        "walkover mientras existan "
                        "jugadores por definir."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ---------------------------------
        # WO solamente sin juego
        # ---------------------------------

        if match.sets.exists():

            return Response(
                {
                    "detail": (
                        "No se puede registrar un "
                        "walkover porque el partido "
                        "ya tiene sets registrados. "
                        "Debe utilizar Retiro."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ---------------------------------
        # No puede estar cancelado
        # ---------------------------------

        if (
            match.status
            == Match.Status.CANCELADO
        ):

            return Response(
                {
                    "detail": (
                        "No se puede registrar un "
                        "walkover en un partido "
                        "cancelado."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ---------------------------------
        # Ganador
        # ---------------------------------

        (
            winner,
            error_response,
        ) = self._get_winner_from_request(
            request,
            match,
        )

        if error_response is not None:
            return error_response

        # ---------------------------------
        # Finalizar
        # ---------------------------------

        match.winner_player = (
            winner
        )

        match.status = (
            Match.Status.FINALIZADO
        )

        match.resolution_type = (
            Match.ResolutionType.WALKOVER
        )

        # Compatibilidad temporal
        match.is_walkover = True

        match.save(
            update_fields=[
                "winner_player",
                "status",
                "resolution_type",
                "is_walkover",
            ]
        )

        # ---------------------------------
        # Eliminación directa:
        # avanzar ganador.
        #
        # En escalerilla no modifica
        # ningún bracket.
        # ---------------------------------

        MatchSetSerializer.sync_winner_with_next_match(
            match
        )

        create_audit_log(
            user=request.user,
            action="UPDATE",
            instance=match,
        )

        serializer = (
            self.get_serializer(
                match
            )
        )

        return Response(
            serializer.data,
            status=(
                status.HTTP_200_OK
            ),
        )

    # =====================================================
    # RETIRO
    # =====================================================

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="retirement",
    )
    def retirement(
        self,
        request,
        pk=None,
    ):
        """
        Finaliza un partido por RETIRO.

        Reglas:

        - deben existir dos jugadores;
        - puede ocurrir aunque no exista un set completo;
        - puede conservar sets completos e incompletos;
        - debe indicarse ganador;
        - finaliza inmediatamente;
        - en eliminación directa avanza al ganador.

        Un retiro puede ocurrir, por ejemplo:

            5-2 RET

            6-4, 2-1 RET

            6-4, 4-6, 5-3 RET

        También puede registrarse sin marcador parcial
        cuando el retiro ocurre al comienzo del partido.
        """

        match = (
            self.get_object()
        )

        # ---------------------------------
        # Proteger ronda posterior
        # ---------------------------------

        MatchSetSerializer.ensure_result_is_editable(
            match
        )

        # ---------------------------------
        # Jugadores
        # ---------------------------------

        if (
            match.player1_id is None
            or match.player2_id is None
        ):

            return Response(
                {
                    "detail": (
                        "No se puede registrar un "
                        "retiro mientras existan "
                        "jugadores por definir."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # # ---------------------------------
        # # Debe existir juego
        # # ---------------------------------

        # if (
        #     not match.sets.exists()
        # ):

        #     return Response(
        #         {
        #             "detail": (
        #                 "No se puede registrar un retiro "
        #                 "sin sets disputados. Si el jugador "
        #                 "no se presentó, debe registrar "
        #                 "un walkover."
        #             )
        #         },
        #         status=(
        #             status.HTTP_400_BAD_REQUEST
        #         ),
        #     )

        # ---------------------------------
        # Partido cancelado
        # ---------------------------------

        if (
            match.status
            == Match.Status.CANCELADO
        ):

            return Response(
                {
                    "detail": (
                        "No se puede registrar un "
                        "retiro en un partido cancelado."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ---------------------------------
        # Ganador
        # ---------------------------------

        (
            winner,
            error_response,
        ) = self._get_winner_from_request(
            request,
            match,
        )

        if error_response is not None:
            return error_response

        # ---------------------------------
        # Finalizar
        # ---------------------------------

        match.winner_player = (
            winner
        )

        match.status = (
            Match.Status.FINALIZADO
        )

        match.resolution_type = (
            Match.ResolutionType.RETIREMENT
        )

        match.is_walkover = False

        match.save(
            update_fields=[
                "winner_player",
                "status",
                "resolution_type",
                "is_walkover",
            ]
        )

        # ---------------------------------
        # Eliminación directa:
        # avanzar ganador.
        # ---------------------------------

        MatchSetSerializer.sync_winner_with_next_match(
            match
        )

        create_audit_log(
            user=request.user,
            action="UPDATE",
            instance=match,
        )

        serializer = (
            self.get_serializer(
                match
            )
        )

        return Response(
            serializer.data,
            status=(
                status.HTTP_200_OK
            ),
        )

        # =====================================================
    # RESTABLECER RESOLUCIÓN
    # =====================================================

    @action(
        detail=True,
        methods=[
            "post",
        ],
        url_path="reset-resolution",
    )
    def reset_resolution(
        self,
        request,
        pk=None,
    ):
        """
        Restablece un partido definido por
        WALKOVER o RETIRO a resolución NORMAL.

        Reglas:

        - permite corregir errores administrativos;
        - conserva los sets existentes;
        - recalcula el resultado a partir de los sets;
        - en eliminación directa corrige también
          la propagación hacia la siguiente ronda;
        - no permite modificar el resultado si la
          ronda posterior ya comenzó.
        """

        match = (
            self.get_object()
        )

        # ---------------------------------
        # Proteger ronda posterior
        # ---------------------------------

        MatchSetSerializer.ensure_result_is_editable(
            match
        )

        # ---------------------------------
        # Partido cancelado
        # ---------------------------------

        if (
            match.status
            == Match.Status.CANCELADO
        ):

            return Response(
                {
                    "detail": (
                        "No se puede restablecer "
                        "la resolución de un "
                        "partido cancelado."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ---------------------------------
        # Ya es NORMAL
        # ---------------------------------

        if (
            match.resolution_type
            == Match.ResolutionType.NORMAL
            and not match.is_walkover
        ):

            return Response(
                {
                    "detail": (
                        "El partido ya tiene "
                        "resolución normal."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ---------------------------------
        # Volver a NORMAL
        # ---------------------------------

        match.resolution_type = (
            Match.ResolutionType.NORMAL
        )

        match.is_walkover = False

        match.save(
            update_fields=[
                "resolution_type",
                "is_walkover",
            ]
        )

        # ---------------------------------
        # Recalcular desde los sets
        #
        # 0 sets:
        # PROGRAMADO / sin ganador
        #
        # sets sin ganador del partido:
        # EN_JUEGO / sin ganador
        #
        # 2 sets ganados:
        # FINALIZADO / ganador calculado
        # ---------------------------------

        MatchSetSerializer.recalculate_match_result(
            match
        )

        match.refresh_from_db()

        # ---------------------------------
        # Auditoría
        # ---------------------------------

        create_audit_log(
            user=request.user,
            action="UPDATE",
            instance=match,
        )

        serializer = (
            self.get_serializer(
                match
            )
        )

        return Response(
            serializer.data,
            status=(
                status.HTTP_200_OK
            ),
        )

class MatchSetViewSet(
    AuditModelViewSet
):

    queryset = (
        MatchSet.objects
        .select_related(
            "match",
            "match__competition_category",
            "match__competition_category__competition",
            "match__player1",
            "match__player2",
            "match__next_match",
        )
        .all()
    )

    serializer_class = (
        MatchSetSerializer
    )

    permission_classes = [
        CompetitionPermission
    ]

    # =====================================================
    # ELIMINAR SET
    # =====================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):

        instance = (
            self.get_object()
        )

        match = (
            instance.match
        )

        # ---------------------------------
        # 1. Protección del cuadro
        # ---------------------------------

        MatchSetSerializer.ensure_result_is_editable(
            match
        )

        # ---------------------------------
        # 2. Solo puede eliminarse
        #    el último set registrado
        # ---------------------------------

        later_set_exists = (
            MatchSet.objects
            .filter(
                match=match,
                set_number__gt=(
                    instance.set_number
                ),
            )
            .exists()
        )

        if later_set_exists:

            return Response(
                {
                    "detail": (
                        "No se puede eliminar este set "
                        "porque existen sets posteriores. "
                        "Debe eliminar primero el último "
                        "set registrado."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        return super().destroy(
            request,
            *args,
            **kwargs,
        )

    # =====================================================
    # POST DELETE
    # =====================================================

    def perform_destroy(
        self,
        instance,
    ):

        match = (
            instance.match
        )

        super().perform_destroy(
            instance
        )

        MatchSetSerializer.recalculate_match_result(
            match
        )
class StandingViewSet(AuditModelViewSet):

    queryset = Standing.objects.select_related(
        "competition_category",
        "competition_category__competition",
        "competition_category__category",
        "player",
    ).all()

    serializer_class = StandingSerializer
    permission_classes = [CompetitionPermission]
    
    
    