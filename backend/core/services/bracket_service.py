import math
import random

from django.db import transaction
from rest_framework.exceptions import ValidationError

from core.models import (
    CompetitionCategory,
    Match,
    Registration,
)


class BracketService:
    """
    Servicio encargado de generar cuadros
    de eliminación directa.
    """

    # =====================================================
    # GENERAR CUADRO
    # =====================================================

    @classmethod
    @transaction.atomic
    def generate_bracket(
        cls,
        competition_category: CompetitionCategory,
    ):
        """
        Genera el cuadro completo para una
        CompetitionCategory.

        Solo considera inscripciones CONFIRMADAS.
        """

        cls._validate_competition_category(
            competition_category
        )

        registrations = list(
            Registration.objects
            .select_related("player")
            .filter(
                competition_category=(
                    competition_category
                ),
                status="CONFIRMADA",
            )
        )

        cls._validate_registrations(
            competition_category,
            registrations,
        )

        bracket_size = (
            cls._calculate_bracket_size(
                len(registrations)
            )
        )

        first_round_slots = (
            cls._build_first_round_slots(
                registrations,
                bracket_size,
            )
        )

        rounds = (
            cls._create_empty_bracket(
                competition_category,
                bracket_size,
            )
        )

        cls._assign_first_round_players(
            rounds[1],
            first_round_slots,
        )

        cls._connect_rounds(
            rounds
        )

        cls._resolve_first_round_byes(
            rounds[1]
        )

        return rounds

    # =====================================================
    # VALIDACIONES
    # =====================================================

    @staticmethod
    def _validate_competition_category(
        competition_category,
    ):
        competition = (
            competition_category.competition
        )

        if (
            competition.type
            != "ELIMINACION_DIRECTA"
        ):
            raise ValidationError(
                {
                    "competition_category": (
                        "Solo se puede generar un cuadro "
                        "para competencias de eliminación "
                        "directa."
                    )
                }
            )

        if (
            competition_category
            .matches
            .exists()
        ):
            raise ValidationError(
                {
                    "bracket": (
                        "El cuadro de esta categoría "
                        "ya fue generado."
                    )
                }
            )

    @staticmethod
    def _validate_registrations(
        competition_category,
        registrations,
    ):
        player_count = len(
            registrations
        )

        if (
            player_count
            < competition_category.minimum_players
        ):
            raise ValidationError(
                {
                    "players": (
                        "No existe el número mínimo "
                        "de jugadores confirmados para "
                        "generar el cuadro."
                    )
                }
            )

        if (
            player_count
            > competition_category.max_players
        ):
            raise ValidationError(
                {
                    "players": (
                        "La cantidad de jugadores "
                        "confirmados supera el máximo "
                        "permitido para esta categoría."
                    )
                }
            )

        if player_count < 2:
            raise ValidationError(
                {
                    "players": (
                        "Se requieren al menos dos "
                        "jugadores para generar "
                        "un cuadro."
                    )
                }
            )

        seeds = [
            registration.seed
            for registration
            in registrations
            if registration.seed is not None
        ]

        if (
            len(seeds)
            != len(set(seeds))
        ):
            raise ValidationError(
                {
                    "seed": (
                        "No puede existir más de un "
                        "jugador con el mismo número "
                        "de cabeza de serie."
                    )
                }
            )

        if any(
            seed < 1
            for seed in seeds
        ):
            raise ValidationError(
                {
                    "seed": (
                        "Los números de cabeza de "
                        "serie deben ser mayores "
                        "que cero."
                    )
                }
            )

        if any(
            seed > player_count
            for seed in seeds
        ):
            raise ValidationError(
                {
                    "seed": (
                        "Un número de cabeza de serie "
                        "no puede ser mayor que la "
                        "cantidad de jugadores "
                        "confirmados."
                    )
                }
            )

    # =====================================================
    # TAMAÑO DEL CUADRO
    # =====================================================

    @staticmethod
    def _calculate_bracket_size(
        player_count,
    ):
        """
        Devuelve la potencia de 2 inmediatamente
        superior o igual al número de jugadores.

        5  -> 8
        8  -> 8
        9  -> 16
        16 -> 16
        33 -> 64
        """

        return 2 ** math.ceil(
            math.log2(
                player_count
            )
        )

    # =====================================================
    # ORDEN DE SEEDS
    # =====================================================

    @classmethod
    def _generate_seed_order(
        cls,
        bracket_size,
    ):
        """
        Genera las posiciones base de los seeds.

        La estructura permite que:

        - 1 y 2 estén en mitades opuestas.
        - Los seeds superiores queden distribuidos.
        - Los enfrentamientos completos respeten
          1 vs N, 2 vs N-1, etc.
        """

        if bracket_size == 2:

            return [
                1,
                2,
            ]

        order = [
            1,
            2,
        ]

        current_size = 2

        while (
            current_size
            < bracket_size
        ):
            new_size = (
                current_size * 2
            )

            new_order = []

            for seed in order:

                new_order.append(
                    seed
                )

                new_order.append(
                    new_size + 1 - seed
                )

            order = (
                new_order
            )

            current_size = (
                new_size
            )

        return (
            cls._rearrange_seed_order(
                order
            )
        )

    @staticmethod
    def _rearrange_seed_order(
        order,
    ):
        """
        Reordena las parejas para mantener al
        seed 1 y seed 2 en mitades opuestas.

        La pareja individual permanece intacta.
        """

        if len(order) <= 4:

            return order

        pairs = [
            order[
                index:index + 2
            ]
            for index in range(
                0,
                len(order),
                2,
            )
        ]

        first_pair = (
            pairs[0]
        )

        seed_two_pair = next(
            pair
            for pair in pairs
            if 2 in pair
        )

        remaining = [
            pair
            for pair in pairs
            if pair
            not in (
                first_pair,
                seed_two_pair,
            )
        ]

        half_count = (
            len(pairs) // 2
        )

        top = [
            first_pair
        ]

        bottom = [
            seed_two_pair
        ]

        for pair in remaining:

            if (
                len(top)
                < half_count
            ):
                top.append(
                    pair
                )

            else:
                bottom.insert(
                    0,
                    pair,
                )

        result = []

        for pair in (
            top + bottom
        ):
            result.extend(
                pair
            )

        return result

    # =====================================================
    # CONSTRUCCIÓN DE PRIMERA RONDA
    # =====================================================

    @classmethod
    def _build_first_round_slots(
        cls,
        registrations,
        bracket_size,
    ):
        """
        Construye las posiciones de primera ronda.

        Casos:

        1. Todos tienen seed.
        2. Algunos tienen seed.
        3. Nadie tiene seed.

        También distribuye correctamente los BYE
        para evitar partidos BYE vs BYE.
        """

        seeded = {
            registration.seed:
                registration
            for registration
            in registrations
            if registration.seed is not None
        }

        unseeded = [
            registration
            for registration
            in registrations
            if registration.seed is None
        ]

        # =================================================
        # NADIE TIENE SEED
        # =================================================

        if not seeded:

            return (
                cls._build_random_slots_with_byes(
                    unseeded,
                    bracket_size,
                )
            )

        seed_order = (
            cls._generate_seed_order(
                bracket_size
            )
        )

        slots = [
            None
            for _ in range(
                bracket_size
            )
        ]

        # =================================================
        # TODOS TIENEN SEED
        # =================================================

        if (
            len(seeded)
            == len(registrations)
        ):

            for (
                position,
                expected_seed,
            ) in enumerate(
                seed_order
            ):

                slots[position] = (
                    seeded.get(
                        expected_seed
                    )
                )

            return slots

        # =================================================
        # ALGUNOS TIENEN SEED
        # =================================================

        seed_positions = {
            seed:
                position
            for (
                position,
                seed,
            ) in enumerate(
                seed_order
            )
        }

        for (
            seed,
            registration,
        ) in seeded.items():

            position = (
                seed_positions.get(
                    seed
                )
            )

            if position is None:

                raise ValidationError(
                    {
                        "seed": (
                            "No fue posible ubicar "
                            "una cabeza de serie "
                            "dentro del cuadro."
                        )
                    }
                )

            slots[position] = (
                registration
            )

        random.shuffle(
            unseeded
        )

        cls._fill_partial_seeded_slots(
            slots,
            unseeded,
        )

        return slots

    # =====================================================
    # SIN SEEDS + BYE
    # =====================================================

    @staticmethod
    def _build_random_slots_with_byes(
        registrations,
        bracket_size,
    ):
        """
        Genera un cuadro aleatorio sin seeds.

        Garantiza que los BYE estén repartidos
        individualmente y nunca se produzca:

            BYE vs BYE

        cuando existe un número válido de jugadores.

        Ejemplo 6 jugadores en cuadro de 8:

            J1 vs BYE
            J2 vs BYE
            J3 vs J4
            J5 vs J6
        """

        registrations = list(
            registrations
        )

        random.shuffle(
            registrations
        )

        bye_count = (
            bracket_size
            - len(registrations)
        )

        pairs = []

        # ---------------------------------
        # Primero asignamos un jugador
        # a cada BYE.
        # ---------------------------------

        for _ in range(
            bye_count
        ):

            player = (
                registrations.pop()
            )

            if random.choice(
                [
                    True,
                    False,
                ]
            ):

                pairs.append(
                    [
                        player,
                        None,
                    ]
                )

            else:

                pairs.append(
                    [
                        None,
                        player,
                    ]
                )

        # ---------------------------------
        # Los jugadores restantes
        # forman partidos normales.
        # ---------------------------------

        while registrations:

            player1 = (
                registrations.pop()
            )

            player2 = (
                registrations.pop()
            )

            pairs.append(
                [
                    player1,
                    player2,
                ]
            )

        # ---------------------------------
        # El orden de los partidos también
        # es aleatorio.
        # ---------------------------------

        random.shuffle(
            pairs
        )

        slots = []

        for pair in pairs:

            slots.extend(
                pair
            )

        return slots

    # =====================================================
    # SEEDS PARCIALES
    # =====================================================

    @staticmethod
    def _fill_partial_seeded_slots(
        slots,
        unseeded,
    ):
        """
        Completa un cuadro que tiene algunos seeds.

        Objetivos:

        - No mover los seeds de sus posiciones.
        - Evitar partidos BYE vs BYE.
        - Dar prioridad de BYE a jugadores sembrados.
        - Distribuir aleatoriamente los no sembrados.
        """

        pairs = [
            [
                index,
                index + 1,
            ]
            for index in range(
                0,
                len(slots),
                2,
            )
        ]

        random.shuffle(
            unseeded
        )

        # ---------------------------------
        # 1. Evitar parejas completamente
        # vacías.
        #
        # Una pareja sin ningún seed recibe
        # primero un jugador.
        # ---------------------------------

        for (
            left,
            right,
        ) in pairs:

            if (
                slots[left] is None
                and slots[right] is None
                and unseeded
            ):

                selected_position = (
                    random.choice(
                        [
                            left,
                            right,
                        ]
                    )
                )

                slots[
                    selected_position
                ] = (
                    unseeded.pop()
                )

        # ---------------------------------
        # 2. Priorizar completar partidos
        # que NO contienen un cabeza de serie.
        #
        # Así los BYE que queden disponibles
        # favorecen a los seeds.
        # ---------------------------------

        non_seed_empty_positions = []

        seeded_empty_positions = []

        for (
            left,
            right,
        ) in pairs:

            left_registration = (
                slots[left]
            )

            right_registration = (
                slots[right]
            )

            left_seeded = (
                left_registration
                is not None
                and left_registration.seed
                is not None
            )

            right_seeded = (
                right_registration
                is not None
                and right_registration.seed
                is not None
            )

            if (
                slots[left] is None
            ):

                if right_seeded:

                    seeded_empty_positions.append(
                        (
                            right_registration.seed,
                            left,
                        )
                    )

                else:

                    non_seed_empty_positions.append(
                        left
                    )

            if (
                slots[right] is None
            ):

                if left_seeded:

                    seeded_empty_positions.append(
                        (
                            left_registration.seed,
                            right,
                        )
                    )

                else:

                    non_seed_empty_positions.append(
                        right
                    )

        random.shuffle(
            non_seed_empty_positions
        )

        # ---------------------------------
        # Seeds de menor prioridad reciben
        # rival primero.
        #
        # De esta forma Seed 1 queda entre
        # los primeros candidatos a BYE.
        # ---------------------------------

        seeded_empty_positions.sort(
            key=lambda item: (
                item[0]
            ),
            reverse=True,
        )

        fill_positions = (
            non_seed_empty_positions
            +
            [
                position
                for (
                    seed,
                    position,
                )
                in seeded_empty_positions
            ]
        )

        for registration in (
            unseeded
        ):

            if not fill_positions:
                break

            position = (
                fill_positions.pop(
                    0
                )
            )

            slots[position] = (
                registration
            )

    # =====================================================
    # CREAR TODAS LAS RONDAS
    # =====================================================

    @staticmethod
    def _create_empty_bracket(
        competition_category,
        bracket_size,
    ):
        """
        Crea todos los partidos del cuadro.

        8 jugadores:

        R1 -> 4 partidos
        R2 -> 2 partidos
        R3 -> 1 partido
        """

        total_rounds = int(
            math.log2(
                bracket_size
            )
        )

        rounds = {}

        for round_number in range(
            1,
            total_rounds + 1,
        ):

            matches_in_round = (
                bracket_size
                // (
                    2 ** round_number
                )
            )

            rounds[
                round_number
            ] = []

            for position in range(
                1,
                matches_in_round + 1,
            ):

                match = (
                    Match.objects.create(
                        competition_category=(
                            competition_category
                        ),
                        round=(
                            round_number
                        ),
                        bracket_position=(
                            position
                        ),
                        status=(
                            Match.Status.PROGRAMADO
                        ),
                    )
                )

                rounds[
                    round_number
                ].append(
                    match
                )

        return rounds

    # =====================================================
    # ASIGNAR PRIMERA RONDA
    # =====================================================

    @staticmethod
    def _assign_first_round_players(
        first_round,
        slots,
    ):
        for (
            index,
            match,
        ) in enumerate(
            first_round
        ):

            slot_index = (
                index * 2
            )

            registration1 = (
                slots[
                    slot_index
                ]
            )

            registration2 = (
                slots[
                    slot_index + 1
                ]
            )

            match.player1 = (
                registration1.player
                if registration1
                else None
            )

            match.player2 = (
                registration2.player
                if registration2
                else None
            )

            match.save(
                update_fields=[
                    "player1",
                    "player2",
                ]
            )

    # =====================================================
    # CONECTAR RONDAS
    # =====================================================

    @staticmethod
    def _connect_rounds(
        rounds,
    ):
        total_rounds = len(
            rounds
        )

        for round_number in range(
            1,
            total_rounds,
        ):

            current_round = (
                rounds[
                    round_number
                ]
            )

            next_round = (
                rounds[
                    round_number + 1
                ]
            )

            for (
                index,
                match,
            ) in enumerate(
                current_round
            ):

                next_match_index = (
                    index // 2
                )

                next_match = (
                    next_round[
                        next_match_index
                    ]
                )

                next_match_slot = (
                    1
                    if index % 2 == 0
                    else 2
                )

                match.next_match = (
                    next_match
                )

                match.next_match_slot = (
                    next_match_slot
                )

                match.save(
                    update_fields=[
                        "next_match",
                        "next_match_slot",
                    ]
                )

    # =====================================================
    # RESOLVER BYE
    # =====================================================

    @classmethod
    def _resolve_first_round_byes(
        cls,
        first_round,
    ):
        """
        Resuelve automáticamente los partidos
        de primera ronda con exactamente
        un jugador.

        Ejemplo:

            Carlos vs BYE

        Carlos pasa automáticamente a la
        siguiente ronda.
        """

        for match in first_round:

            has_player1 = (
                match.player1
                is not None
            )

            has_player2 = (
                match.player2
                is not None
            )

            # Ambos tienen jugador.
            if (
                has_player1
                and has_player2
            ):
                continue

            # Ninguno tiene jugador.
            if (
                not has_player1
                and not has_player2
            ):
                continue

            winner = (
                match.player1
                if has_player1
                else match.player2
            )

            match.winner_player = (
                winner
            )

            match.status = (
                Match.Status.FINALIZADO
            )

            match.save(
                update_fields=[
                    "winner_player",
                    "status",
                ]
            )

            cls._advance_winner(
                match
            )
    # =====================================================
    # AVANZAR GANADOR PÚBLICAMENTE
    # =====================================================

    @classmethod
    @transaction.atomic
    def advance_winner(
        cls,
        match,
    ):
        """
        Avanza el ganador de un partido al siguiente
        partido del cuadro.

        Este método solo puede utilizarse en
        competencias de eliminación directa.
        """

        competition = (
            match
            .competition_category
            .competition
        )

        if (
            competition.type
            != "ELIMINACION_DIRECTA"
        ):
            return

        if (
            match.status
            != Match.Status.FINALIZADO
        ):
            return

        if (
            match.winner_player is None
        ):
            return

        cls._advance_winner(
            match
        )


    # =====================================================
    # AVANZAR GANADOR
    # =====================================================

    @classmethod
    def _advance_winner(
        cls,
        match,
    ):
        """
        Propaga automáticamente el ganador
        al siguiente partido del cuadro.

        No permite sobrescribir un jugador
        diferente que ya haya avanzado al slot.
        """

        if (
            match.next_match is None
            or match.winner_player is None
        ):
            return

        next_match = (
            match.next_match
        )

        if (
            match.next_match_slot
            == 1
        ):

            current_player = (
                next_match.player1
            )

            if (
                current_player is not None
                and current_player
                != match.winner_player
            ):
                raise ValidationError(
                    {
                        "bracket": (
                            "No se puede modificar el "
                            "ganador porque el siguiente "
                            "partido ya contiene otro "
                            "jugador en esa posición."
                        )
                    }
                )

            next_match.player1 = (
                match.winner_player
            )

            update_field = (
                "player1"
            )

        elif (
            match.next_match_slot
            == 2
        ):

            current_player = (
                next_match.player2
            )

            if (
                current_player is not None
                and current_player
                != match.winner_player
            ):
                raise ValidationError(
                    {
                        "bracket": (
                            "No se puede modificar el "
                            "ganador porque el siguiente "
                            "partido ya contiene otro "
                            "jugador en esa posición."
                        )
                    }
                )

            next_match.player2 = (
                match.winner_player
            )

            update_field = (
                "player2"
            )

        else:

            return

        next_match.save(
            update_fields=[
                update_field
            ]
        )