from itertools import combinations

from django.db import transaction
from rest_framework import serializers

from core.models import CompetitionCategory, Match, Registration, Standing


class LadderService:
    """Servicio único para generación y standings de escalerilla."""

    STAT_FIELDS = (
        "matches_played",
        "matches_won",
        "matches_lost",
        "sets_won",
        "sets_lost",
        "games_won",
        "games_lost",
        "points",
        "walkovers_won",
        "walkovers_lost",
    )

    @staticmethod
    def get_confirmed_participants(competition_category):
        return (
            Registration.objects.filter(
                competition_category=competition_category,
                status="CONFIRMADA",
            )
            .select_related("player")
            .order_by("player__last_name", "player__first_name", "player__id")
        )

    @classmethod
    def is_ladder(cls, competition_category):
        return competition_category.competition.type == "ESCALERILLA"

    @classmethod
    def is_generated_ladder_match(cls, match):
        """
        Identifica los partidos creados por generate_ladder con la estructura
        disponible actualmente. No existe una marca persistente específica;
        un partido manual con exactamente esta estructura es indistinguible.
        """
        return (
            cls.is_ladder(match.competition_category)
            and match.player1_id is not None
            and match.player2_id is not None
            and match.round is None
            and match.bracket_position is None
            and match.next_match_id is None
            and match.next_match_slot is None
        )

    @staticmethod
    def _generated_matches_queryset(competition_category):
        return Match.objects.filter(
            competition_category=competition_category,
            player1__isnull=False,
            player2__isnull=False,
            round__isnull=True,
            bracket_position__isnull=True,
            next_match__isnull=True,
            next_match_slot__isnull=True,
        )

    @classmethod
    def get_ladder_deletion_status(cls, competition_category, matches=None):
        if matches is None:
            category_matches = list(
                Match.objects.filter(competition_category=competition_category)
                .select_related("competition_category__competition")
                .prefetch_related("sets")
            )
        else:
            category_matches = list(matches)

        matches = [
            match for match in category_matches
            if cls.is_generated_ladder_match(match)
        ]

        scheduled_matches_count = sum(
            1
            for match in matches
            if match.scheduled_date_time is not None or match.court_id is not None
        )

        if not matches:
            return {
                "can_delete": False,
                "scheduled_matches_count": 0,
                "delete_block_reason": "La escalerilla no ha sido generada.",
            }

        if len(matches) != len(category_matches):
            return {
                "can_delete": False,
                "scheduled_matches_count": scheduled_matches_count,
                "delete_block_reason": (
                    "La categoría contiene partidos que no pueden identificarse "
                    "de forma segura como parte de la escalerilla generada."
                ),
            }

        for match in matches:
            has_sporting_activity = (
                match.sets.exists()
                or match.status != Match.Status.PROGRAMADO
                or match.resolution_type != Match.ResolutionType.NORMAL
                or match.is_walkover
                or match.winner_player_id is not None
            )
            if has_sporting_activity:
                return {
                    "can_delete": False,
                    "scheduled_matches_count": scheduled_matches_count,
                    "delete_block_reason": (
                        "La escalerilla no puede eliminarse porque ya existen "
                        "partidos disputados o resultados registrados."
                    ),
                }

        return {
            "can_delete": True,
            "scheduled_matches_count": scheduled_matches_count,
            "delete_block_reason": None,
        }

    @classmethod
    @transaction.atomic
    def delete_ladder(cls, competition_category):
        locked_category = (
            CompetitionCategory.objects.select_for_update()
            .select_related("competition")
            .get(pk=competition_category.pk)
        )
        if not cls.is_ladder(locked_category):
            raise serializers.ValidationError(
                {"detail": "Esta categoría no pertenece a una escalerilla."}
            )

        category_matches_queryset = (
            Match.objects.filter(competition_category=locked_category)
            .select_for_update()
            .select_related("competition_category__competition")
            .prefetch_related("sets")
        )
        category_matches = list(category_matches_queryset)
        matches = [
            match for match in category_matches
            if cls.is_generated_ladder_match(match)
        ]
        deletion_status = cls.get_ladder_deletion_status(
            locked_category,
            category_matches,
        )
        if not deletion_status["can_delete"]:
            raise serializers.ValidationError(
                {"detail": deletion_status["delete_block_reason"]}
            )

        deleted_matches = len(matches)
        deleted_scheduled_matches = deletion_status["scheduled_matches_count"]

        # MatchSet se elimina por CASCADE desde Match.
        Match.objects.filter(pk__in=[match.pk for match in matches]).delete()
        deleted_standings, _ = Standing.objects.filter(
            competition_category=locked_category
        ).delete()

        return {
            "deleted_matches": deleted_matches,
            "deleted_scheduled_matches": deleted_scheduled_matches,
            "deleted_standings": deleted_standings,
        }

    @staticmethod
    def standing_sort_key(standing):
        return (
            -standing.points,
            -(standing.sets_won - standing.sets_lost),
            -(standing.games_won - standing.games_lost),
            -standing.matches_won,
            standing.player.last_name.casefold(),
            standing.player.first_name.casefold(),
            standing.player_id,
        )

    @classmethod
    @transaction.atomic
    def generate_ladder(cls, competition_category):
        competition_category = (
            CompetitionCategory.objects.select_for_update()
            .select_related("competition")
            .get(pk=competition_category.pk)
        )
        if not cls.is_ladder(competition_category):
            raise serializers.ValidationError(
                {"detail": "Esta categoría no pertenece a una escalerilla."}
            )

        if Match.objects.filter(competition_category=competition_category).exists():
            raise serializers.ValidationError(
                {"detail": "La escalerilla ya fue generada para esta categoría."}
            )

        players = [
            registration.player
            for registration in cls.get_confirmed_participants(competition_category)
        ]
        if len(players) < 2:
            raise serializers.ValidationError(
                {"detail": "Se requieren al menos 2 participantes confirmados."}
            )

        matches = [
            Match(
                competition_category=competition_category,
                player1=player1,
                player2=player2,
                status=Match.Status.PROGRAMADO,
                round=None,
                bracket_position=None,
                next_match=None,
                next_match_slot=None,
                scheduled_date_time=None,
                court=None,
            )
            for player1, player2 in combinations(players, 2)
        ]
        Match.objects.bulk_create(matches)
        cls._sync_standings(competition_category, players)
        cls.recalculate_standings(competition_category)
        return matches

    @classmethod
    def _sync_standings(cls, competition_category, players):
        player_ids = [player.id for player in players]
        Standing.objects.filter(competition_category=competition_category).exclude(
            player_id__in=player_ids
        ).delete()
        existing_ids = set(
            Standing.objects.filter(
                competition_category=competition_category,
                player_id__in=player_ids,
            ).values_list("player_id", flat=True)
        )
        Standing.objects.bulk_create(
            [
                Standing(competition_category=competition_category, player=player)
                for player in players
                if player.id not in existing_ids
            ]
        )

    @classmethod
    @transaction.atomic
    def recalculate_standings(cls, competition_category):
        if not cls.is_ladder(competition_category):
            return []

        players = [
            registration.player
            for registration in cls.get_confirmed_participants(competition_category)
        ]
        cls._sync_standings(competition_category, players)
        standings = {
            standing.player_id: standing
            for standing in Standing.objects.select_for_update()
            .filter(competition_category=competition_category)
            .select_related("player")
        }

        for standing in standings.values():
            for field in cls.STAT_FIELDS:
                setattr(standing, field, 0)
            standing.position = None

        participant_ids = set(standings)
        matches = (
            Match.objects.filter(
                competition_category=competition_category,
                status=Match.Status.FINALIZADO,
                player1_id__in=participant_ids,
                player2_id__in=participant_ids,
            )
            .select_related("winner_player")
            .prefetch_related("sets")
        )
        for match in matches:
            if not match.winner_player_id:
                continue
            winner = standings[match.winner_player_id]
            loser_id = (
                match.player2_id
                if match.winner_player_id == match.player1_id
                else match.player1_id
            )
            loser = standings[loser_id]
            winner.matches_played += 1
            loser.matches_played += 1
            winner.matches_won += 1
            loser.matches_lost += 1

            if (
                match.resolution_type == Match.ResolutionType.WALKOVER
                or match.is_walkover
            ):
                winner.sets_won += 2
                loser.sets_lost += 2
                winner.games_won += 12
                loser.games_lost += 12
                winner.points += 4
                loser.points += 1
                winner.walkovers_won += 1
                loser.walkovers_lost += 1
                continue

            player1_sets = 0
            player2_sets = 0
            for match_set in match.sets.all():
                # Los puntos del Super Tie-Break no representan juegos.
                if not match_set.is_super_tie_break:
                    standings[match.player1_id].games_won += match_set.games_player1
                    standings[match.player1_id].games_lost += match_set.games_player2
                    standings[match.player2_id].games_won += match_set.games_player2
                    standings[match.player2_id].games_lost += match_set.games_player1
                if match_set.is_incomplete:
                    continue
                if match_set.games_player1 > match_set.games_player2:
                    player1_sets += 1
                    standings[match.player1_id].sets_won += 1
                    standings[match.player2_id].sets_lost += 1
                else:
                    player2_sets += 1
                    standings[match.player2_id].sets_won += 1
                    standings[match.player1_id].sets_lost += 1

            if match.resolution_type == Match.ResolutionType.RETIREMENT:
                winner.points += 4
                loser.points += 1
            else:
                winner_sets = (
                    player1_sets
                    if match.winner_player_id == match.player1_id
                    else player2_sets
                )
                loser_sets = player2_sets if match.winner_player_id == match.player1_id else player1_sets
                if winner_sets == 2 and loser_sets == 1:
                    winner.points += 3
                    loser.points += 2
                else:
                    winner.points += 4
                    loser.points += 1

        ordered = sorted(
            standings.values(),
            key=cls.standing_sort_key,
        )
        for position, standing in enumerate(ordered, start=1):
            standing.position = position
        if ordered:
            Standing.objects.bulk_update(
                ordered, [*cls.STAT_FIELDS, "position"]
            )
        return ordered

    @classmethod
    def recalculate_for_match(cls, match):
        competition_category = match.competition_category
        if cls.is_ladder(competition_category):
            return cls.recalculate_standings(competition_category)
        return []
