from rest_framework import serializers

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

class PlayerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True
    )

    class Meta:
        model = Player
        fields = [
            "id",
            "user",
            "category",
            "rut",
            "first_name",
            "last_name",
            "birth_date",
            "email",
            "phone",
        ]
        read_only_fields = ["id", "email"]
class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            "id",
            "name",
            "type",
            "start_date",
            "end_date",
            "status",
            "registration_deadline",
        ]
        read_only_fields = ["id"]
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]
        read_only_fields = ["id"]
        

class CompetitionCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = CompetitionCategory
        fields = [
            "id",
            "competition",
            "category",
            "max_players",
            "minimum_players",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        instance = self.instance

        max_players = data.get(
            "max_players",
            instance.max_players if instance else None,
        )

        minimum_players = data.get(
            "minimum_players",
            instance.minimum_players if instance else None,
        )

        if (
            max_players is not None
            and minimum_players is not None
            and minimum_players > max_players
        ):
            raise serializers.ValidationError(
                {
                    "minimum_players": (
                        "El número mínimo de jugadores "
                        "no puede ser mayor al máximo."
                    )
                }
            )

        return data
class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Registration
        fields = [
            "id",
            "competition_category",
            "player",
            "registration_date",
            "status",
            "seed",
        ]
        read_only_fields = [
            "id",
            "registration_date",
        ]

    def validate(self, data):

        # ---------------------------------
        # Obtener valores actuales
        # ---------------------------------

        instance = self.instance

        player = data.get(
            "player",
            instance.player if instance else None,
        )

        competition_category = data.get(
            "competition_category",
            (
                instance.competition_category
                if instance
                else None
            ),
        )

        # ---------------------------------
        # 1. El jugador debe pertenecer a
        #    la categoría de la competencia
        # ---------------------------------

        if (
            player is not None
            and competition_category is not None
            and player.category_id
            != competition_category.category_id
        ):
            raise serializers.ValidationError(
                {
                    "competition_category": (
                        "El jugador solo puede inscribirse "
                        "en una categoría que corresponda "
                        "a su categoría actual."
                    )
                }
            )

        # ---------------------------------
        # Las siguientes reglas corresponden
        # solamente a la creación de una
        # inscripción.
        # ---------------------------------

        if instance is None:

            competition = (
                competition_category.competition
            )

            # ---------------------------------
            # 2. Estado de la competencia
            # ---------------------------------

            request = self.context.get("request")
            user = (
                request.user
                if request is not None
                else None
            )

            status = competition.status

            if status == "EN_CURSO":
                if (
                    user is None
                    or not user.is_authenticated
                    or user.role.name != "Administrador"
                ):
                    raise serializers.ValidationError(
                        {
                            "competition_category": (
                                "Solo un Administrador "
                                "puede registrar jugadores "
                                "en una competencia "
                                "en curso."
                            )
                        }
                    )

            elif status not in [
                "PENDIENTE",
                "ABIERTA",
            ]:
                raise serializers.ValidationError(
                    {
                        "competition_category": (
                            "No se pueden registrar "
                            "jugadores en una competencia "
                            "finalizada o cancelada."
                        )
                    }
                )

            # ---------------------------------
            # 3. Cupos máximos
            # ---------------------------------

            registrations_count = (
                Registration.objects.filter(
                    competition_category=competition_category,
                )
                .exclude(status="CANCELADA")
                .count()
            )

            if (
                registrations_count
                >= competition_category.max_players
            ):
                raise serializers.ValidationError(
                    {
                        "competition_category": (
                            "Se ha alcanzado el máximo "
                            "de jugadores permitido "
                            "para esta categoría."
                        )
                    }
                )

        return data

class CourtSerializer(serializers.ModelSerializer):

    class Meta:
        model = Court
        fields = [
            "id",
            "name",
            "status",
        ]
        read_only_fields = ["id"]
        
        
class MatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Match
        fields = [
            "id",
            "competition_category",
            "court",
            "player1",
            "player2",
            "winner_player",
            "scheduled_date_time",
            "status",
            "round",
            "is_walkover",
        ]
        read_only_fields = ["id"]

    def validate(self, data):

    # ---------------------------------
    # Obtener valores actuales
    # ---------------------------------
    # En PATCH, si un campo no viene en data,
    # usamos el valor que ya tiene la instancia.

        instance = self.instance

        competition_category = data.get(
            "competition_category",
            instance.competition_category if instance else None,
        )

        player1 = data.get(
            "player1",
            instance.player1 if instance else None,
        )

        player2 = data.get(
            "player2",
            instance.player2 if instance else None,
        )

        winner_player = data.get(
            "winner_player",
            instance.winner_player if instance else None,
        )

        round_number = data.get(
            "round",
            instance.round if instance else None,
        )

        is_walkover = data.get(
            "is_walkover",
            instance.is_walkover if instance else False,
        )

        # ---------------------------------
        # 1. Player 1 debe pertenecer
        #    a la categoría del partido
        # ---------------------------------

        if (
            player1 is not None
            and competition_category is not None
            and player1.category_id
            != competition_category.category_id
        ):
            raise serializers.ValidationError(
                {
                    "player1": (
                        "El jugador no pertenece a "
                        "la categoría del partido."
                    )
                }
            )

        # ---------------------------------
        # 2. Player 2 debe pertenecer
        #    a la categoría del partido
        # ---------------------------------

        if (
            player2 is not None
            and competition_category is not None
            and player2.category_id
            != competition_category.category_id
        ):
            raise serializers.ValidationError(
                {
                    "player2": (
                        "El jugador no pertenece a "
                        "la categoría del partido."
                    )
                }
            )

        # ---------------------------------
        # 3. Un jugador no puede enfrentarse
        #    contra sí mismo
        # ---------------------------------

        if (
            player1 is not None
            and player2 is not None
            and player1.id == player2.id
        ):
            raise serializers.ValidationError(
                {
                    "player2": (
                        "Un jugador no puede enfrentarse "
                        "contra sí mismo."
                    )
                }
            )

        # ---------------------------------
        # 4. El ganador debe ser uno de
        #    los jugadores del partido
        # ---------------------------------

        if winner_player is not None:

            valid_winners = []

            if player1 is not None:
                valid_winners.append(player1)

            if player2 is not None:
                valid_winners.append(player2)

            if winner_player not in valid_winners:
                raise serializers.ValidationError(
                    {
                        "winner_player": (
                            "El ganador debe ser uno de "
                            "los jugadores del partido."
                        )
                    }
                )

        # ---------------------------------
        # 5. Round
        # ---------------------------------

        competition_type = None

        if competition_category is not None:
            competition_type = (
                competition_category.competition.type
            )

        if competition_type == "ELIMINACION_DIRECTA":

            if round_number is None:
                raise serializers.ValidationError(
                    {
                        "round": (
                            "La ronda es obligatoria "
                            "para eliminación directa."
                        )
                    }
                )

        elif competition_type == "ESCALERILLA":

            if round_number is not None:
                raise serializers.ValidationError(
                    {
                        "round": (
                            "La ronda no corresponde "
                            "a una competencia de escalerilla."
                        )
                    }
                )

        # ---------------------------------
        # 6. Walkover
        # ---------------------------------

        if is_walkover and player2 is None:
            raise serializers.ValidationError(
                {
                    "is_walkover": (
                        "Un walkover requiere dos jugadores."
                    )
                }
            )

        return data


class MatchSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = MatchSet
        fields = [
            "id",
            "match",
            "set_number",
            "games_player1",
            "games_player2",
            "is_super_tie_break",
        ]
        read_only_fields = ["id"]

    def validate(self, data):

        # ---------------------------------
        # Obtener valores actuales
        # ---------------------------------

        instance = self.instance

        set_number = data.get(
            "set_number",
            instance.set_number if instance else None,
        )

        games_player1 = data.get(
            "games_player1",
            instance.games_player1 if instance else None,
        )

        games_player2 = data.get(
            "games_player2",
            instance.games_player2 if instance else None,
        )

        is_super_tie_break = data.get(
            "is_super_tie_break",
            instance.is_super_tie_break if instance else False,
        )

        # ---------------------------------
        # 1. Número de set
        # ---------------------------------

        if set_number < 1:
            raise serializers.ValidationError(
                {
                    "set_number": (
                        "El número de set debe ser "
                        "mayor que 0."
                    )
                }
            )

        # ---------------------------------
        # 2. Solo el SET 3 puede ser
        #    super tie-break
        # ---------------------------------

        if is_super_tie_break and set_number != 3:
            raise serializers.ValidationError(
                {
                    "is_super_tie_break": (
                        "Solo el tercer set puede "
                        "ser un super tie-break."
                    )
                }
            )

        # ---------------------------------
        # 3. No puede existir empate
        # ---------------------------------

        if games_player1 == games_player2:
            raise serializers.ValidationError(
                {
                    "games": (
                        "Un set no puede terminar "
                        "en empate."
                    )
                }
            )

        # ---------------------------------
        # 4. SUPER TIE-BREAK
        # ---------------------------------

        if is_super_tie_break:

            winner = max(
                games_player1,
                games_player2,
            )

            loser = min(
                games_player1,
                games_player2,
            )

            if winner < 10:
                raise serializers.ValidationError(
                    {
                        "games": (
                            "El super tie-break debe "
                            "alcanzar al menos 10 puntos."
                        )
                    }
                )

            if winner - loser < 2:
                raise serializers.ValidationError(
                    {
                        "games": (
                            "El super tie-break debe "
                            "ganarse por una diferencia "
                            "mínima de 2 puntos."
                        )
                    }
                )

            return data

        # ---------------------------------
        # 5. SET NORMAL
        # ---------------------------------

        winner = max(
            games_player1,
            games_player2,
        )

        loser = min(
            games_player1,
            games_player2,
        )

        # 6-0, 6-1, 6-2, 6-3, 6-4
        if winner == 6 and loser <= 4:
            return data

        # 7-5
        if winner == 7 and loser == 5:
            return data

        # 7-6
        if winner == 7 and loser == 6:
            return data

        raise serializers.ValidationError(
            {
                "games": (
                    "El resultado no corresponde "
                    "a un marcador válido de tenis."
                )
            }
        )
        
class StandingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Standing
        fields = [
            "id",
            "competition_category",
            "player",
            "matches_played",
            "matches_won",
            "matches_lost",
            "walkovers_won",
            "walkovers_lost",
            "sets_won",
            "sets_lost",
            "games_won",
            "games_lost",
            "points",
            "position",
        ]

        read_only_fields = [
            "id",
            "matches_played",
            "matches_won",
            "matches_lost",
            "walkovers_won",
            "walkovers_lost",
            "sets_won",
            "sets_lost",
            "games_won",
            "games_lost",
            "points",
            "position",
        ]

    def validate(self, data):

        competition_category = data.get(
            "competition_category"
        )

        player = data.get(
            "player"
        )

        # ---------------------------------
        # El jugador debe pertenecer a la
        # categoría de la competencia
        # ---------------------------------

        if (
            competition_category is not None
            and player is not None
            and player.category_id
            != competition_category.category_id
        ):
            raise serializers.ValidationError(
                {
                    "player": (
                        "El jugador no pertenece "
                        "a la categoría de la competencia."
                    )
                }
            )

        # ---------------------------------
        # Evitar duplicados
        # ---------------------------------

        queryset = Standing.objects.filter(
            competition_category=competition_category,
            player=player,
        )

        # En PATCH excluimos el registro actual
        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk
            )

        if queryset.exists():
            raise serializers.ValidationError(
                {
                    "player": (
                        "El jugador ya tiene un "
                        "standing en esta categoría "
                        "de competencia."
                    )
                }
            )

        return data