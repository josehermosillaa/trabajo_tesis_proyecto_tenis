import re

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from rest_framework import serializers
from core.services.bracket_service import BracketService
from core.services.match_scheduling_service import MatchSchedulingService
from authentication.models import Role

from .models import (
    Category,
    Competition,
    CompetitionCategory,
    Player,
    Registration,
    Court,
    Match,
    MatchSet,
    Standing,
)


# =========================================================
# PLAYER
# =========================================================

class PlayerSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source="user.username",
        required=False,
    )

    email = serializers.EmailField(
        source="user.email",
        required=False,
    )

    password = serializers.CharField(
        write_only=True,
        required=False,
        style={
            "input_type": "password",
        },
    )

    class Meta:
        model = Player

        fields = [
            "id",
            "user",
            "username",
            "email",
            "password",
            "category",
            "rut",
            "first_name",
            "last_name",
            "birth_date",
            "phone",
        ]

        read_only_fields = [
            "id",
            "user",
        ]

    # ---------------------------------
    # Username único
    # ---------------------------------

    def validate_username(self, value):

        User = get_user_model()

        queryset = User.objects.filter(
            username=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.user_id
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "El nombre de usuario ya está registrado."
            )

        return value

    # ---------------------------------
    # Email único
    # ---------------------------------

    def validate_email(self, value):

        User = get_user_model()

        queryset = User.objects.filter(
            email__iexact=value
        )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.user_id
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "El correo electrónico ya está registrado."
            )

        return value

    # ---------------------------------
    # Fecha de nacimiento
    # ---------------------------------

    def validate_birth_date(self, value):

        if value is None:
            return value

        today = timezone.localdate()

        if value > today:
            raise serializers.ValidationError(
                "La fecha de nacimiento no puede ser futura."
            )

        try:
            minimum_birth_date = today.replace(
                year=today.year - 10
            )
        except ValueError:
            minimum_birth_date = today.replace(
                year=today.year - 10,
                day=28,
            )

        if value > minimum_birth_date:
            raise serializers.ValidationError(
                "El jugador debe tener al menos 10 años."
            )

        return value

    # ---------------------------------
    # RUT chileno
    # ---------------------------------

    def validate_rut(self, value):

        if not value:
            return value

        rut = (
            value
            .replace(".", "")
            .replace("-", "")
            .upper()
            .strip()
        )

        if len(rut) < 2:
            raise serializers.ValidationError(
                "El RUT ingresado no es válido."
            )

        body = rut[:-1]
        verifier = rut[-1]

        if not body.isdigit():
            raise serializers.ValidationError(
                "El RUT ingresado no es válido."
            )

        total = 0
        multiplier = 2

        for digit in reversed(body):

            total += int(digit) * multiplier

            multiplier += 1

            if multiplier > 7:
                multiplier = 2

        remainder = 11 - (total % 11)

        if remainder == 11:
            expected_verifier = "0"

        elif remainder == 10:
            expected_verifier = "K"

        else:
            expected_verifier = str(remainder)

        if verifier != expected_verifier:
            raise serializers.ValidationError(
                "El RUT ingresado no es válido."
            )

        return f"{int(body)}-{verifier}"

    # ---------------------------------
    # Teléfono
    # ---------------------------------

    def validate_phone(self, value):

        if not value:
            return value

        if not re.fullmatch(
            r"\+569\d{8}",
            value
        ):
            raise serializers.ValidationError(
                "El teléfono debe contener un "
                "número móvil chileno válido."
            )

        return value

    # ---------------------------------
    # Validaciones generales
    # ---------------------------------

    def validate(self, data):

        if self.instance is None:

            user_data = data.get(
                "user",
                {}
            )

            username = user_data.get(
                "username"
            )

            email = user_data.get(
                "email"
            )

            password = data.get(
                "password"
            )

            errors = {}

            if not username:
                errors["username"] = (
                    "El nombre de usuario es obligatorio."
                )

            if not email:
                errors["email"] = (
                    "El correo electrónico es obligatorio."
                )

            if not password:
                errors["password"] = (
                    "La contraseña temporal es obligatoria."
                )

            if errors:
                raise serializers.ValidationError(
                    errors
                )

            try:
                validate_password(
                    password
                )

            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    {
                        "password": list(
                            exc.messages
                        )
                    }
                )

        return data

    # ---------------------------------
    # Crear User + Player
    # ---------------------------------

    @transaction.atomic
    def create(
        self,
        validated_data
    ):

        User = get_user_model()

        user_data = validated_data.pop(
            "user"
        )

        password = validated_data.pop(
            "password"
        )

        try:
            player_role = Role.objects.get(
                name="Jugador"
            )

        except Role.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "role": (
                        "No existe el rol Jugador "
                        "en el sistema."
                    )
                }
            )

        user = User.objects.create_user(
            username=user_data["username"],
            email=user_data["email"],
            password=password,
            first_name=validated_data[
                "first_name"
            ],
            last_name=validated_data[
                "last_name"
            ],
            role=player_role,
        )

        player = Player.objects.create(
            user=user,
            **validated_data,
        )

        return player

    # ---------------------------------
    # Actualizar Player + User
    # ---------------------------------

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):

        user_data = validated_data.pop(
            "user",
            {},
        )

        validated_data.pop(
            "password",
            None,
        )

        user = instance.user

        if "username" in user_data:
            user.username = user_data[
                "username"
            ]

        if "email" in user_data:
            user.email = user_data[
                "email"
            ]

        if "first_name" in validated_data:
            user.first_name = validated_data[
                "first_name"
            ]

        if "last_name" in validated_data:
            user.last_name = validated_data[
                "last_name"
            ]

        user.save()

        return super().update(
            instance,
            validated_data,
        )


# =========================================================
# COMPETITION
# =========================================================

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

        read_only_fields = [
            "id",
        ]

    def validate(self, data):

        instance = self.instance
        today = timezone.localdate()

        start_date = data.get(
            "start_date",
            instance.start_date if instance else None,
        )

        end_date = data.get(
            "end_date",
            instance.end_date if instance else None,
        )

        registration_deadline = data.get(
            "registration_deadline",
            (
                instance.registration_deadline
                if instance
                else None
            ),
        )

        # ---------------------------------
        # 1. Fecha término >= inicio
        # ---------------------------------

        if (
            start_date is not None
            and end_date is not None
            and end_date < start_date
        ):
            raise serializers.ValidationError(
                {
                    "end_date": (
                        "La fecha de término no puede ser "
                        "anterior a la fecha de inicio."
                    )
                }
            )

        # ---------------------------------
        # 2. Cierre inscripción <= inicio
        # ---------------------------------

        if (
            registration_deadline is not None
            and start_date is not None
            and registration_deadline > start_date
        ):
            raise serializers.ValidationError(
                {
                    "registration_deadline": (
                        "La fecha límite de inscripción "
                        "no puede ser posterior a la "
                        "fecha de inicio."
                    )
                }
            )

        # ---------------------------------
        # 3. Creación
        # ---------------------------------

        if instance is None:

            if (
                start_date is not None
                and start_date < today
            ):
                raise serializers.ValidationError(
                    {
                        "start_date": (
                            "La fecha de inicio no puede "
                            "ser anterior a la fecha actual."
                        )
                    }
                )

            if (
                registration_deadline is not None
                and registration_deadline < today
            ):
                raise serializers.ValidationError(
                    {
                        "registration_deadline": (
                            "La fecha límite de inscripción "
                            "no puede ser anterior a la "
                            "fecha actual."
                        )
                    }
                )

        # ---------------------------------
        # 4. Edición
        # ---------------------------------

        else:

            if "start_date" in data:

                new_start_date = data[
                    "start_date"
                ]

                if (
                    new_start_date
                    != instance.start_date
                    and new_start_date < today
                ):
                    raise serializers.ValidationError(
                        {
                            "start_date": (
                                "No se puede cambiar la "
                                "fecha de inicio por una "
                                "fecha anterior a la actual."
                            )
                        }
                    )

            if "registration_deadline" in data:

                new_deadline = data[
                    "registration_deadline"
                ]

                if (
                    new_deadline
                    != instance.registration_deadline
                    and new_deadline < today
                ):
                    raise serializers.ValidationError(
                        {
                            "registration_deadline": (
                                "No se puede cambiar la "
                                "fecha límite de inscripción "
                                "por una fecha anterior a "
                                "la actual."
                            )
                        }
                    )

        return data


# =========================================================
# CATEGORY
# =========================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
        ]

        read_only_fields = [
            "id",
        ]


# =========================================================
# COMPETITION CATEGORY
# =========================================================

class CompetitionCategorySerializer(
    serializers.ModelSerializer
):

    occupied_slots = (
        serializers.SerializerMethodField()
    )

    available_slots = (
        serializers.SerializerMethodField()
    )

    registered_players = (
        serializers.SerializerMethodField()
    )

    class Meta:
        model = CompetitionCategory

        fields = [
            "id",
            "competition",
            "category",
            "max_players",
            "minimum_players",
            "occupied_slots",
            "available_slots",
            "registered_players",
        ]

        read_only_fields = [
            "id",
            "occupied_slots",
            "available_slots",
            "registered_players",
        ]

    def get_occupied_slots(
        self,
        obj
    ):

        return (
            obj.registrations
            .exclude(
                status="CANCELADA"
            )
            .count()
        )

    def get_available_slots(
        self,
        obj
    ):

        occupied = (
            obj.registrations
            .exclude(
                status="CANCELADA"
            )
            .count()
        )

        return max(
            obj.max_players - occupied,
            0,
        )

    def get_registered_players(
        self,
        obj
    ):

        registrations = obj.registrations.all()
        request = self.context.get("request")

        if (
            request is not None
            and request.user.is_authenticated
            and request.user.role.name == "Jugador"
        ):
            registrations = registrations.filter(status="CONFIRMADA")
        else:
            registrations = registrations.exclude(status="CANCELADA")

        registrations = registrations.select_related("player")

        return [
            {
                "id":
                    registration.player.id,

                "first_name":
                    registration.player.first_name,

                "last_name":
                    registration.player.last_name,

                "status":
                    registration.status,

            }
            for registration
            in registrations
        ]

    def validate(self, data):

        instance = self.instance

        max_players = data.get(
            "max_players",
            (
                instance.max_players
                if instance
                else None
            ),
        )

        minimum_players = data.get(
            "minimum_players",
            (
                instance.minimum_players
                if instance
                else None
            ),
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


class CompetitionCategoryDiscoverySerializer(serializers.ModelSerializer):
    """Datos de descubrimiento sin nombres ni estados de participantes."""

    occupied_slots = serializers.SerializerMethodField()
    available_slots = serializers.SerializerMethodField()

    class Meta:
        model = CompetitionCategory
        fields = [
            "id",
            "competition",
            "category",
            "max_players",
            "minimum_players",
            "occupied_slots",
            "available_slots",
        ]
        read_only_fields = fields

    def get_occupied_slots(self, obj):
        return obj.registrations.exclude(status="CANCELADA").count()

    def get_available_slots(self, obj):
        return max(obj.max_players - self.get_occupied_slots(obj), 0)


# =========================================================
# REGISTRATION
# =========================================================

class RegistrationSerializer(serializers.ModelSerializer):

    player = serializers.PrimaryKeyRelatedField(
        queryset=Player.objects.all(),
        required=False,
    )

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
        validators = []

    def validate(self, data):

        instance = self.instance

        request = self.context.get(
            "request"
        )

        user = (
            request.user
            if request is not None
            else None
        )

        role = (
            user.role.name
            if (
                user is not None
                and user.is_authenticated
            )
            else None
        )

        # ---------------------------------
        # Determinar jugador
        # ---------------------------------

        if instance is None:

            if role == "Jugador":

                try:
                    player = user.player

                except Player.DoesNotExist:
                    raise serializers.ValidationError(
                        {
                            "player": (
                                "El usuario autenticado "
                                "no tiene un perfil de "
                                "jugador asociado."
                            )
                        }
                    )

                data["player"] = player

            else:

                player = data.get(
                    "player"
                )

                if player is None:
                    raise serializers.ValidationError(
                        {
                            "player": (
                                "Debe seleccionar "
                                "un jugador."
                            )
                        }
                    )

        else:

            player = data.get(
                "player",
                instance.player,
            )

        competition_category = data.get(
            "competition_category",
            (
                instance.competition_category
                if instance
                else None
            ),
        )

        if competition_category is None:
            raise serializers.ValidationError(
                {
                    "competition_category": (
                        "Debe seleccionar una "
                        "categoría de competencia."
                    )
                }
            )

        # ---------------------------------
        # 1. Categoría jugador
        # ---------------------------------

        if (
            player.category_id
            != competition_category.category_id
            and role not in [
                "Administrador",
                "Organizador",
            ]
        ):
            raise serializers.ValidationError(
                {
                    "competition_category": (
                        "El jugador solo puede "
                        "inscribirse en una categoría "
                        "que corresponda a su "
                        "categoría actual."
                    )
                }
            )

        # ---------------------------------
        # Reglas de creación
        # ---------------------------------

        if instance is None:

            competition = (
                competition_category.competition
            )

            status = competition.status

            # ---------------------------------
            # 2. Estado competencia
            # ---------------------------------

            if status == "EN_CURSO":

                if role != "Administrador":
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
            # 3. Fecha límite
            # ---------------------------------

            today = timezone.localdate()

            if (
                competition.registration_deadline
                < today
                and role != "Administrador"
            ):
                raise serializers.ValidationError(
                    {
                        "competition_category": (
                            "La fecha límite de "
                            "inscripción ya ha finalizado. "
                            "Solo un Administrador puede "
                            "registrar jugadores después "
                            "del cierre."
                        )
                    }
                )

            # ---------------------------------
            # 4. Cupos
            # ---------------------------------

            registrations_count = (
                Registration.objects.filter(
                    competition_category=(
                        competition_category
                    ),
                )
                .exclude(
                    status="CANCELADA"
                )
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

            # ---------------------------------
            # 6. Jugador no decide estado/seed
            # ---------------------------------

            if role == "Jugador":

                data["status"] = (
                    "CONFIRMADA"
                )

                data["seed"] = None

        # ---------------------------------
        # 5. Duplicados vigentes por competencia
        # ---------------------------------

        resulting_status = data.get(
            "status",
            (
                instance.status
                if instance
                else "PENDIENTE"
            ),
        )

        if resulting_status != "CANCELADA":

            duplicate_registrations = (
                Registration.objects.filter(
                    competition_category__competition=(
                        competition_category.competition
                    ),
                    player=player,
                )
                .exclude(
                    status="CANCELADA"
                )
            )

            if instance is not None:
                duplicate_registrations = (
                    duplicate_registrations.exclude(
                        pk=instance.pk
                    )
                )

            if duplicate_registrations.exists():
                raise serializers.ValidationError(
                    {
                        "player": (
                            "El jugador ya tiene una "
                            "inscripción vigente en esta "
                            "competencia."
                        )
                    }
                )

        return data


# =========================================================
# COURT
# =========================================================

class CourtSerializer(serializers.ModelSerializer):

    class Meta:
        model = Court

        fields = [
            "id",
            "name",
            "status",
        ]

        read_only_fields = [
            "id",
        ]


# =========================================================
# MATCH
# =========================================================

class MatchSerializer(serializers.ModelSerializer):

    sets = serializers.SerializerMethodField(
        read_only=True
    )

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
            "bracket_position",
            "next_match",
            "next_match_slot",
            "is_walkover",
            "resolution_type",
            "sets",
        ]

        read_only_fields = [
            "id",
            "bracket_position",
            "next_match",
            "next_match_slot",
            "sets",
        ]

    # =====================================================
    # SETS PARA VISUALIZACIÓN DEL CUADRO
    # =====================================================

    def get_sets(
        self,
        obj,
    ):

        return [
            {
                "id": match_set.id,
                "set_number": (
                    match_set.set_number
                ),
                "games_player1": (
                    match_set.games_player1
                ),
                "games_player2": (
                    match_set.games_player2
                ),
                "is_super_tie_break": (
                    match_set.is_super_tie_break
                ),
            }
            for match_set in (
                obj.sets
                .all()
                .order_by("set_number")
            )
        ]

    # =====================================================
    # VALIDACIÓN
    # =====================================================

    def validate(
        self,
        data,
    ):

        instance = self.instance

        if (
            instance is not None
            and BracketService
            .is_generated_bracket_match(instance)
        ):
            protected_fields = {
                "competition_category",
                "player1",
                "player2",
                "winner_player",
                "status",
                "round",
                "bracket_position",
                "next_match",
                "next_match_slot",
                "resolution_type",
                "is_walkover",
            }
            requested_protected_fields = (
                protected_fields.intersection(
                    self.initial_data.keys()
                )
            )

            if requested_protected_fields:
                raise serializers.ValidationError(
                    {
                        "detail": (
                            "Este partido pertenece a un cuadro "
                            "de eliminación directa. Desde este "
                            "endpoint solo puede modificarse su "
                            "programación y cancha."
                        )
                    }
                )

        competition_category = data.get(
            "competition_category",
            (
                instance.competition_category
                if instance
                else None
            ),
        )

        player1 = data.get(
            "player1",
            (
                instance.player1
                if instance
                else None
            ),
        )

        player2 = data.get(
            "player2",
            (
                instance.player2
                if instance
                else None
            ),
        )

        winner_player = data.get(
            "winner_player",
            (
                instance.winner_player
                if instance
                else None
            ),
        )

        status = data.get(
            "status",
            (
                instance.status
                if instance
                else Match.Status.PROGRAMADO
            ),
        )

        round_number = data.get(
            "round",
            (
                instance.round
                if instance
                else None
            ),
        )

        is_walkover = data.get(
            "is_walkover",
            (
                instance.is_walkover
                if instance
                else False
            ),
        )

        scheduling_fields_present = (
            "scheduled_date_time" in data
            or
            "court" in data
        )

        scheduled_date_time = data.get(
            "scheduled_date_time",
            instance.scheduled_date_time if instance else None,
        )

        court = data.get(
            "court",
            instance.court if instance else None,
        )

        # ---------------------------------
        # Datos mínimos
        # ---------------------------------

        if competition_category is None:

            raise serializers.ValidationError(
                {
                    "competition_category": (
                        "Debe indicar la categoría "
                        "de la competencia."
                    )
                }
            )

        # ---------------------------------
        # Programación de partidos
        # ---------------------------------

        if scheduling_fields_present:

            if (
                player1 is None
                or
                player2 is None
            ):

                raise serializers.ValidationError(
                    {
                        "scheduled_date_time": (
                            "No se puede programar un partido "
                            "con BYE o participantes por definir."
                        )
                    }
                )

            if status in [
                Match.Status.EN_JUEGO,
                Match.Status.FINALIZADO,
                Match.Status.CANCELADO,
            ]:

                raise serializers.ValidationError(
                    {
                        "scheduled_date_time": (
                            "Solo se puede modificar la programación "
                            "de un partido en estado PROGRAMADO."
                        )
                    }
                )

            if scheduled_date_time is not None:

                if (
                    court is not None
                    and MatchSchedulingService.has_court_conflict(
                        scheduled_date_time,
                        court,
                        instance,
                    )
                ):
                    raise serializers.ValidationError(
                        {
                            "court": (
                                "La cancha seleccionada ya tiene un partido "
                                "programado en ese horario."
                            )
                        }
                    )

                if MatchSchedulingService.has_player_conflict(
                    scheduled_date_time,
                    player1,
                    player2,
                    instance,
                ):
                    raise serializers.ValidationError(
                        {
                            "scheduled_date_time": (
                                "Uno de los jugadores ya tiene otro partido "
                                "programado en ese horario."
                            )
                        }
                    )

        # /*
        #  * IMPORTANTE:
        #  *
        #  * Los partidos generados automáticamente
        #  * para rondas futuras pueden tener
        #  * player1/player2 en null.
        #  *
        #  * Sin embargo, un partido creado
        #  * manualmente desde la API sigue
        #  * necesitando player1.
        #  */

        if (
            player1 is None
            and instance is None
        ):

            raise serializers.ValidationError(
                {
                    "player1": (
                        "Debe indicar el primer jugador."
                    )
                }
            )

        # ---------------------------------
        # 1. Player 1 debe estar confirmado
        # ---------------------------------

        if player1 is not None:

            player1_confirmed = (
                Registration.objects.filter(
                    competition_category=(
                        competition_category
                    ),
                    player=player1,
                    status="CONFIRMADA",
                )
                .exists()
            )

            if not player1_confirmed:

                raise serializers.ValidationError(
                    {
                        "player1": (
                            "El jugador debe tener una "
                            "inscripción confirmada para "
                            "participar en esta competencia."
                        )
                    }
                )

        # ---------------------------------
        # 2. Player 2 debe estar confirmado
        # ---------------------------------

        if player2 is not None:

            player2_confirmed = (
                Registration.objects.filter(
                    competition_category=(
                        competition_category
                    ),
                    player=player2,
                    status="CONFIRMADA",
                )
                .exists()
            )

            if not player2_confirmed:

                raise serializers.ValidationError(
                    {
                        "player2": (
                            "El jugador debe tener una "
                            "inscripción confirmada para "
                            "participar en esta competencia."
                        )
                    }
                )

        # ---------------------------------
        # 5. Jugador contra sí mismo
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
        # 6. Ganador válido
        # ---------------------------------

        if winner_player is not None:

            valid_winners = []

            if player1 is not None:

                valid_winners.append(
                    player1
                )

            if player2 is not None:

                valid_winners.append(
                    player2
                )

            if (
                winner_player
                not in valid_winners
            ):

                raise serializers.ValidationError(
                    {
                        "winner_player": (
                            "El ganador debe ser uno "
                            "de los jugadores del partido."
                        )
                    }
                )

        # ---------------------------------
        # 7. Ronda
        # ---------------------------------

        competition_type = (
            competition_category
            .competition
            .type
        )

        if (
            competition_type
            == "ELIMINACION_DIRECTA"
        ):

            if round_number is None:

                raise serializers.ValidationError(
                    {
                        "round": (
                            "La ronda es obligatoria "
                            "para eliminación directa."
                        )
                    }
                )

        elif (
            competition_type
            == "ESCALERILLA"
        ):

            if round_number is not None:

                raise serializers.ValidationError(
                    {
                        "round": (
                            "La ronda no corresponde "
                            "a una competencia de "
                            "escalerilla."
                        )
                    }
                )

        # ---------------------------------
        # 8. Walkover
        # ---------------------------------

        if is_walkover:

            if player2 is None:

                raise serializers.ValidationError(
                    {
                        "is_walkover": (
                            "Un walkover requiere "
                            "dos jugadores."
                        )
                    }
                )

            if winner_player is None:

                raise serializers.ValidationError(
                    {
                        "winner_player": (
                            "Un walkover debe indicar "
                            "al jugador ganador."
                        )
                    }
                )

            data["status"] = (
                Match.Status.FINALIZADO
            )

        # ---------------------------------
        # 9. Partido finalizado
        # ---------------------------------

        elif (
            status
            == Match.Status.FINALIZADO
        ):

            if winner_player is None:

                raise serializers.ValidationError(
                    {
                        "winner_player": (
                            "Un partido finalizado "
                            "debe tener un ganador."
                        )
                    }
                )

        # ---------------------------------
        # 10. Partido no finalizado
        # ---------------------------------

        elif winner_player is not None:

            raise serializers.ValidationError(
                {
                    "winner_player": (
                        "No se puede asignar ganador "
                        "a un partido que todavía "
                        "no está finalizado."
                    )
                }
            )

        return data
# =========================================================
# MATCH SET
# =========================================================

class MatchSetSerializer(
    serializers.ModelSerializer
):

    class Meta:

        model = MatchSet

        fields = [
            "id",
            "match",
            "set_number",
            "games_player1",
            "games_player2",
            "is_super_tie_break",
            "is_incomplete",
        ]

        read_only_fields = [
            "id",
        ]

    # =====================================================
    # HELPERS
    # =====================================================

    @staticmethod
    def get_set_winner(
        games_player1,
        games_player2,
    ):

        if games_player1 > games_player2:
            return 1

        return 2

    # =====================================================
    # ELIMINACIÓN DIRECTA
    # =====================================================

    @staticmethod
    def is_direct_elimination(
        match
    ):

        return (
            match
            .competition_category
            .competition
            .type
            == "ELIMINACION_DIRECTA"
        )

    @staticmethod
    def next_match_has_started(
        match
    ):
        """
        Indica si el partido siguiente ya comenzó
        o ya fue resuelto.
        """

        if (
            match.next_match_id
            is None
        ):
            return False

        next_match = (
            match.next_match
        )

        if (
            next_match.sets.exists()
        ):
            return True

        if (
            next_match.is_walkover
        ):
            return True

        if (
            next_match.status
            in [
                Match.Status.EN_JUEGO,
                Match.Status.FINALIZADO,
                Match.Status.CANCELADO,
            ]
        ):
            return True

        return False

    @classmethod
    def ensure_result_is_editable(
        cls,
        match,
    ):
        """
        Bloquea modificaciones históricas cuando
        la ronda siguiente ya comenzó.

        Solo aplica a eliminación directa.
        """

        if not cls.is_direct_elimination(
            match
        ):
            return

        if (
            match.next_match_id
            is None
        ):
            return

        if cls.next_match_has_started(
            match
        ):

            raise serializers.ValidationError(
                {
                    "match": (
                        "No se puede modificar este "
                        "resultado porque el partido "
                        "de la ronda siguiente ya fue "
                        "iniciado o finalizado."
                    )
                }
            )

    @classmethod
    def sync_winner_with_next_match(
        cls,
        match,
    ):
        """
        Sincroniza el ganador con el partido siguiente.
        """

        if not cls.is_direct_elimination(
            match
        ):
            return

        if (
            match.next_match_id
            is None
        ):
            return

        next_match = (
            match.next_match
        )

        if cls.next_match_has_started(
            match
        ):
            return

        winner = (
            match.winner_player
            if (
                match.status
                == Match.Status.FINALIZADO
            )
            else None
        )

        if (
            match.next_match_slot
            == 1
        ):

            next_match.player1 = (
                winner
            )

            next_match.save(
                update_fields=[
                    "player1",
                ]
            )

        elif (
            match.next_match_slot
            == 2
        ):

            next_match.player2 = (
                winner
            )

            next_match.save(
                update_fields=[
                    "player2",
                ]
            )

    # =====================================================
    # RECALCULAR PARTIDO
    # =====================================================

    @classmethod
    def recalculate_match_result(
        cls,
        match,
    ):

        sets = (
            match.sets
            .all()
            .order_by(
                "set_number"
            )
        )

        player1_sets = 0
        player2_sets = 0

        for match_set in sets:

            # ---------------------------------------------
            # Un set incompleto NO cuenta como set ganado.
            #
            # Ejemplo:
            # 6-4, 2-1 RET
            #
            # Solo el 6-4 cuenta como set terminado.
            # ---------------------------------------------

            if (
                match_set.is_incomplete
            ):
                continue

            if (
                match_set.games_player1
                >
                match_set.games_player2
            ):

                player1_sets += 1

            else:

                player2_sets += 1

        # =================================================
        # PLAYER 1 GANÓ
        # =================================================

        if (
            player1_sets >= 2
        ):

            match.winner_player = (
                match.player1
            )

            match.status = (
                Match.Status.FINALIZADO
            )

            match.resolution_type = (
                Match.ResolutionType.NORMAL
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

            cls.sync_winner_with_next_match(
                match
            )

            return

        # =================================================
        # PLAYER 2 GANÓ
        # =================================================

        if (
            player2_sets >= 2
        ):

            match.winner_player = (
                match.player2
            )

            match.status = (
                Match.Status.FINALIZADO
            )

            match.resolution_type = (
                Match.ResolutionType.NORMAL
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

            cls.sync_winner_with_next_match(
                match
            )

            return

        # =================================================
        # PARTIDO NO FINALIZADO
        # =================================================

        match.winner_player = None

        if sets.exists():

            match.status = (
                Match.Status.EN_JUEGO
            )

        else:

            match.status = (
                Match.Status.PROGRAMADO
            )

        match.resolution_type = (
            Match.ResolutionType.NORMAL
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

        cls.sync_winner_with_next_match(
            match
        )

    # =====================================================
    # VALIDACIÓN
    # =====================================================

    def validate(
        self,
        data,
    ):

        instance = (
            self.instance
        )

        match = data.get(
            "match",
            (
                instance.match
                if instance
                else None
            ),
        )

        set_number = data.get(
            "set_number",
            (
                instance.set_number
                if instance
                else None
            ),
        )

        games_player1 = data.get(
            "games_player1",
            (
                instance.games_player1
                if instance
                else None
            ),
        )

        games_player2 = data.get(
            "games_player2",
            (
                instance.games_player2
                if instance
                else None
            ),
        )

        is_super_tie_break = data.get(
            "is_super_tie_break",
            (
                instance.is_super_tie_break
                if instance
                else False
            ),
        )

        is_incomplete = data.get(
            "is_incomplete",
            (
                instance.is_incomplete
                if instance
                else False
            ),
        )

        # ---------------------------------
        # 1. Partido requerido
        # ---------------------------------

        if match is None:

            raise serializers.ValidationError(
                {
                    "match": (
                        "Debe indicar el partido."
                    )
                }
            )

        # ---------------------------------
        # PROTEGER CUADRO
        # ---------------------------------

        self.ensure_result_is_editable(
            match
        )

        # ---------------------------------
        # 2. Partido cancelado
        # ---------------------------------

        if (
            match.status
            == Match.Status.CANCELADO
        ):

            raise serializers.ValidationError(
                {
                    "match": (
                        "No se pueden registrar sets "
                        "en un partido cancelado."
                    )
                }
            )

        # ---------------------------------
        # 3. Partido resuelto
        # administrativamente
        # ---------------------------------

        if (
            match.is_walkover
            or
            match.resolution_type
            != Match.ResolutionType.NORMAL
        ):

            raise serializers.ValidationError(
                {
                    "match": (
                        "No se pueden registrar o "
                        "modificar sets en un partido "
                        "definido por walkover o retiro."
                    )
                }
            )

        # ---------------------------------
        # 4. BYE
        # ---------------------------------

        if (
            match.player1 is None
            or
            match.player2 is None
        ):

            raise serializers.ValidationError(
                {
                    "match": (
                        "No se pueden registrar sets "
                        "en un partido con BYE o "
                        "jugadores aún por definir."
                    )
                }
            )

        # ---------------------------------
        # 5. Número de set
        # ---------------------------------

        if (
            set_number is None
        ):

            raise serializers.ValidationError(
                {
                    "set_number": (
                        "Debe indicar el número de set."
                    )
                }
            )

        if (
            set_number
            not in [
                1,
                2,
                3,
            ]
        ):

            raise serializers.ValidationError(
                {
                    "set_number": (
                        "El número de set debe ser "
                        "1, 2 o 3."
                    )
                }
            )

        # ---------------------------------
        # 6. Marcadores requeridos
        # ---------------------------------

        if (
            games_player1 is None
            or
            games_player2 is None
        ):

            raise serializers.ValidationError(
                {
                    "games": (
                        "Debe indicar el marcador "
                        "de ambos jugadores."
                    )
                }
            )

        # ---------------------------------
        # 7. STB solamente en Set 3
        # ---------------------------------

        if (
            set_number == 3
        ):

            if (
                not is_super_tie_break
            ):

                raise serializers.ValidationError(
                    {
                        "is_super_tie_break": (
                            "El tercer set debe "
                            "registrarse como un "
                            "super tie-break."
                        )
                    }
                )

        elif (
            is_super_tie_break
        ):

            raise serializers.ValidationError(
                {
                    "is_super_tie_break": (
                        "Solo el tercer set puede "
                        "ser un super tie-break."
                    )
                }
            )

        # =================================================
        # MARCADOR COMPLETO
        # =================================================

        if (
            not is_incomplete
        ):

            # ---------------------------------
            # No empate
            # ---------------------------------

            if (
                games_player1
                == games_player2
            ):

                raise serializers.ValidationError(
                    {
                        "games": (
                            "Un set completo no puede "
                            "terminar en empate."
                        )
                    }
                )

            # ---------------------------------
            # Super Tie-Break completo
            # ---------------------------------

            if (
                is_super_tie_break
            ):

                winner = max(
                    games_player1,
                    games_player2,
                )

                loser = min(
                    games_player1,
                    games_player2,
                )

                if (
                    winner < 10
                ):

                    raise serializers.ValidationError(
                        {
                            "games": (
                                "El super tie-break debe "
                                "alcanzar al menos "
                                "10 puntos."
                            )
                        }
                    )

                if (
                    loser <= 8
                ):

                    if (
                        winner != 10
                    ):

                        raise serializers.ValidationError(
                            {
                                "games": (
                                    "Con 8 puntos o menos "
                                    "del perdedor, el super "
                                    "tie-break debe finalizar "
                                    "exactamente en 10 puntos "
                                    "para el ganador."
                                )
                            }
                        )

                else:

                    if (
                        winner - loser
                        != 2
                    ):

                        raise serializers.ValidationError(
                            {
                                "games": (
                                    "Después de 9-9, el "
                                    "super tie-break debe "
                                    "ganarse exactamente por "
                                    "2 puntos de diferencia."
                                )
                            }
                        )

            # ---------------------------------
            # Set normal completo
            # ---------------------------------

            else:

                winner = max(
                    games_player1,
                    games_player2,
                )

                loser = min(
                    games_player1,
                    games_player2,
                )

                valid_normal_set = (

                    (
                        winner == 6
                        and loser <= 4
                    )

                    or

                    (
                        winner == 7
                        and loser == 5
                    )

                    or

                    (
                        winner == 7
                        and loser == 6
                    )

                )

                if (
                    not valid_normal_set
                ):

                    raise serializers.ValidationError(
                        {
                            "games": (
                                "El resultado no corresponde "
                                "a un marcador válido "
                                "de tenis."
                            )
                        }
                    )

        # =================================================
        # MARCADOR INCOMPLETO
        # =================================================

        else:

            # Un parcial puede estar empatado.
            #
            # Ejemplos válidos:
            #
            # 0-0
            # 1-1
            # 5-2
            # 4-4
            # 2-1
            #
            # Pero no puede ser ya un marcador que
            # representa un set terminado.

            if (
                is_super_tie_break
            ):

                winner = max(
                    games_player1,
                    games_player2,
                )

                loser = min(
                    games_player1,
                    games_player2,
                )

                completed_stb = False

                if (
                    winner >= 10
                ):

                    if (
                        loser <= 8
                        and winner == 10
                    ):

                        completed_stb = True

                    elif (
                        loser >= 9
                        and
                        winner - loser == 2
                    ):

                        completed_stb = True

                if (
                    completed_stb
                ):

                    raise serializers.ValidationError(
                        {
                            "games": (
                                "Este marcador corresponde "
                                "a un super tie-break "
                                "completo. No debe marcarse "
                                "como incompleto."
                            )
                        }
                    )

            else:

                winner = max(
                    games_player1,
                    games_player2,
                )

                loser = min(
                    games_player1,
                    games_player2,
                )

                completed_normal_set = (

                    (
                        winner == 6
                        and loser <= 4
                    )

                    or

                    (
                        winner == 7
                        and loser == 5
                    )

                    or

                    (
                        winner == 7
                        and loser == 6
                    )

                )

                if (
                    completed_normal_set
                ):

                    raise serializers.ValidationError(
                        {
                            "games": (
                                "Este marcador corresponde "
                                "a un set completo. "
                                "No debe marcarse como "
                                "incompleto."
                            )
                        }
                    )

        # ---------------------------------
        # Sets existentes
        # ---------------------------------

        existing_sets = (
            MatchSet.objects
            .filter(
                match=match
            )
        )

        if instance:

            existing_sets = (
                existing_sets.exclude(
                    pk=instance.pk
                )
            )

        existing_by_number = {
            match_set.set_number:
                match_set
            for match_set
            in existing_sets
        }

        # ---------------------------------
        # 8. Set duplicado
        # ---------------------------------

        if (
            set_number
            in existing_by_number
        ):

            raise serializers.ValidationError(
                {
                    "set_number": (
                        "Este número de set ya fue "
                        "registrado para el partido."
                    )
                }
            )

        # ---------------------------------
        # 9. Set 2 requiere Set 1
        # ---------------------------------

        if (
            set_number == 2
            and
            1 not in existing_by_number
        ):

            raise serializers.ValidationError(
                {
                    "set_number": (
                        "No se puede registrar el "
                        "segundo set antes del primero."
                    )
                }
            )

        # ---------------------------------
        # 10. Set 3 requiere 1 y 2
        # ---------------------------------

        if (
            set_number == 3
        ):

            if (
                1 not in existing_by_number
                or
                2 not in existing_by_number
            ):

                raise serializers.ValidationError(
                    {
                        "set_number": (
                            "El tercer set solo puede "
                            "registrarse después de los "
                            "dos primeros sets."
                        )
                    }
                )

            set1 = (
                existing_by_number[1]
            )

            set2 = (
                existing_by_number[2]
            )

            # Ambos deben estar terminados.
            if (
                set1.is_incomplete
                or
                set2.is_incomplete
            ):

                raise serializers.ValidationError(
                    {
                        "set_number": (
                            "No se puede registrar el "
                            "tercer set mientras exista "
                            "un set anterior incompleto."
                        )
                    }
                )

            set1_winner = (
                self.get_set_winner(
                    set1.games_player1,
                    set1.games_player2,
                )
            )

            set2_winner = (
                self.get_set_winner(
                    set2.games_player1,
                    set2.games_player2,
                )
            )

            if (
                set1_winner
                == set2_winner
            ):

                raise serializers.ValidationError(
                    {
                        "set_number": (
                            "El tercer set solo puede "
                            "jugarse cuando el partido "
                            "está igualado a un set."
                        )
                    }
                )

        # ---------------------------------
        # 11. Un set incompleto debe ser
        # siempre el último.
        # ---------------------------------

        for existing_set in (
            existing_sets
        ):

            if (
                existing_set.is_incomplete
                and
                existing_set.set_number
                < set_number
            ):

                raise serializers.ValidationError(
                    {
                        "set_number": (
                            "No se pueden registrar "
                            "sets posteriores a un "
                            "set incompleto."
                        )
                    }
                )

        # ---------------------------------
        # 12. Simulación global
        # ---------------------------------

        simulated_sets = {}

        for (
            number,
            existing_set
        ) in (
            existing_by_number.items()
        ):

            simulated_sets[number] = {
                "games_player1":
                    existing_set
                    .games_player1,

                "games_player2":
                    existing_set
                    .games_player2,

                "is_incomplete":
                    existing_set
                    .is_incomplete,
            }

        simulated_sets[
            set_number
        ] = {
            "games_player1":
                games_player1,

            "games_player2":
                games_player2,

            "is_incomplete":
                is_incomplete,
        }

        numbers = sorted(
            simulated_sets.keys()
        )

        expected_numbers = list(
            range(
                1,
                len(numbers) + 1
            )
        )

        if (
            numbers
            != expected_numbers
        ):

            raise serializers.ValidationError(
                {
                    "set_number": (
                        "Los sets deben registrarse "
                        "en orden consecutivo."
                    )
                }
            )

        player1_sets = 0
        player2_sets = 0

        incomplete_found = False

        for number in numbers:

            simulated_set = (
                simulated_sets[number]
            )

            games1 = (
                simulated_set[
                    "games_player1"
                ]
            )

            games2 = (
                simulated_set[
                    "games_player2"
                ]
            )

            incomplete = (
                simulated_set[
                    "is_incomplete"
                ]
            )

            # ---------------------------------
            # Si ya hubo un set incompleto,
            # no puede existir otro posterior.
            # ---------------------------------

            if incomplete_found:

                raise serializers.ValidationError(
                    {
                        "set_number": (
                            "No puede existir un set "
                            "posterior a un set "
                            "incompleto."
                        )
                    }
                )

            if incomplete:

                incomplete_found = True

                # El parcial no cuenta como
                # set ganado.
                continue

            if (
                games1 > games2
            ):

                player1_sets += 1

            else:

                player2_sets += 1

            if (
                player1_sets >= 2
                or
                player2_sets >= 2
            ):

                if (
                    number
                    != numbers[-1]
                ):

                    raise serializers.ValidationError(
                        {
                            "set_number": (
                                "No se pueden registrar "
                                "sets posteriores porque "
                                "el partido ya finalizó."
                            )
                        }
                    )

        return data

    # =====================================================
    # CREAR
    # =====================================================

    @transaction.atomic
    def create(
        self,
        validated_data,
    ):

        match_set = (
            super().create(
                validated_data
            )
        )

        self.recalculate_match_result(
            match_set.match
        )

        return match_set

    # =====================================================
    # ACTUALIZAR
    # =====================================================

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data,
    ):

        match = (
            instance.match
        )

        self.ensure_result_is_editable(
            match
        )

        match_set = (
            super().update(
                instance,
                validated_data,
            )
        )

        self.recalculate_match_result(
            match_set.match
        )

        return match_set
# =========================================================
# STANDING
# =========================================================

class StandingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Standing

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
            "bracket_position",
            "next_match",
            "next_match_slot",
            "is_walkover",
            "resolution_type",
            "sets",
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
        # Categoría compatible
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
            competition_category=(
                competition_category
            ),
            player=player,
        )

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
