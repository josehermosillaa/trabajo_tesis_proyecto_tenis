from datetime import date, datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from authentication.models import Role
from core.models import Category, Competition, CompetitionCategory, Court, Match, MatchSet, Player, Registration, Standing
from core.serializers import StandingSerializer
from core.services.ladder_service import LadderService


class LadderBackendTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_role = Role.objects.create(name="Administrador")
        self.organizer_role = Role.objects.create(name="Organizador")
        self.player_role = Role.objects.create(name="Jugador")
        User = get_user_model()
        self.admin = User.objects.create_user(username="ladder-admin", role=self.admin_role)
        self.organizer = User.objects.create_user(username="ladder-organizer", role=self.organizer_role)
        self.category = Category.objects.create(name="PRIMERA")
        self.other_category = Category.objects.create(name="SEGUNDA")
        self.competition = self.make_competition("Escalerilla principal")
        self.competition_category = CompetitionCategory.objects.create(
            competition=self.competition,
            category=self.category,
            max_players=20,
            minimum_players=2,
        )
        self.players = [self.make_player(index) for index in range(1, 7)]

    def make_competition(self, name, competition_type="ESCALERILLA"):
        return Competition.objects.create(
            name=name,
            type=competition_type,
            start_date=date(2026, 9, 1),
            end_date=date(2026, 9, 30),
            registration_deadline=date(2026, 8, 31),
        )

    def make_player(self, index, category=None):
        User = get_user_model()
        user = User.objects.create_user(
            username=f"ladder-player-{index}", role=self.player_role
        )
        return Player.objects.create(
            user=user,
            category=category or self.category,
            rut=f"{30000000 + index}-{index % 10}",
            first_name=f"Nombre{index}",
            last_name=f"Apellido{index}",
        )

    def register(self, player, status_value="CONFIRMADA", category=None):
        return Registration.objects.create(
            competition_category=category or self.competition_category,
            player=player,
            status=status_value,
        )

    def test_standing_serializer_uses_confirmed_registration_not_player_category(self):
        exceptional = self.make_player(20, self.other_category)
        self.register(exceptional)
        serializer = StandingSerializer(data={
            "competition_category": self.competition_category.id,
            "player": exceptional.id,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        standing = serializer.save()
        standing.sets_won, standing.sets_lost = 4, 2
        standing.games_won, standing.games_lost = 30, 22
        data = StandingSerializer(standing).data
        self.assertEqual(data["sets_difference"], 2)
        self.assertEqual(data["games_difference"], 8)
        self.assertEqual(set(data), {
            "id", "competition_category", "player", "position",
            "matches_played", "matches_won", "matches_lost", "sets_won",
            "sets_lost", "sets_difference", "games_won", "games_lost",
            "games_difference", "points", "walkovers_won", "walkovers_lost",
        })

        unregistered = self.players[0]
        invalid = StandingSerializer(data={
            "competition_category": self.competition_category.id,
            "player": unregistered.id,
        })
        self.assertFalse(invalid.is_valid())

    def test_generation_counts_only_confirmed_and_is_idempotent(self):
        for player in self.players[:4]:
            self.register(player)
        self.register(self.players[4], "PENDIENTE")
        self.register(self.players[5], "CANCELADA")
        matches = LadderService.generate_ladder(self.competition_category)
        self.assertEqual(len(matches), 6)
        self.assertEqual(Standing.objects.filter(
            competition_category=self.competition_category
        ).count(), 4)
        pairs = set()
        for match in Match.objects.filter(competition_category=self.competition_category):
            self.assertNotEqual(match.player1_id, match.player2_id)
            pairs.add(frozenset((match.player1_id, match.player2_id)))
            self.assertIsNone(match.round)
            self.assertIsNone(match.bracket_position)
            self.assertIsNone(match.next_match_id)
            self.assertIsNone(match.next_match_slot)
            self.assertIsNone(match.court_id)
            self.assertIsNone(match.scheduled_date_time)
        self.assertEqual(len(pairs), 6)
        with self.assertRaisesMessage(ValidationError, "ya fue generada"):
            LadderService.generate_ladder(self.competition_category)

    def test_round_robin_formula_for_two_and_five_players(self):
        for size, expected in ((2, 1), (5, 10)):
            competition = self.make_competition(f"Escalerilla {size}")
            category = CompetitionCategory.objects.create(
                competition=competition, category=self.category,
                max_players=10, minimum_players=2,
            )
            for player in self.players[:size]:
                self.register(player, category=category)
            self.assertEqual(len(LadderService.generate_ladder(category)), expected)

    def test_generate_endpoint_allows_admin_and_rejects_direct_elimination(self):
        self.register(self.players[0])
        self.register(self.players[1])
        self.client.force_authenticate(self.admin)
        response = self.client.post(
            f"/api/competition-categories/{self.competition_category.id}/generate-ladder/"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data["matches"]), 1)

        direct = self.make_competition("Directa", "ELIMINACION_DIRECTA")
        direct_category = CompetitionCategory.objects.create(
            competition=direct, category=self.category,
            max_players=8, minimum_players=2,
        )
        response = self.client.post(
            f"/api/competition-categories/{direct_category.id}/generate-ladder/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_deletes_clean_scheduled_ladder_and_can_generate_again(self):
        registrations = [
            self.register(self.players[0]),
            self.register(self.players[1]),
        ]
        matches = LadderService.generate_ladder(self.competition_category)
        court = Court.objects.create(name="Cancha eliminación escalerilla")
        match = matches[0]
        match.scheduled_date_time = datetime(2026, 9, 10, 18, 30, tzinfo=timezone.utc)
        match.court = court
        match.save(update_fields=["scheduled_date_time", "court"])

        self.client.force_authenticate(self.admin)
        ladder_url = f"/api/competition-categories/{self.competition_category.id}/ladder/"
        detail = self.client.get(ladder_url)
        self.assertTrue(detail.data["can_delete"])
        self.assertIsNone(detail.data["delete_block_reason"])
        self.assertEqual(detail.data["scheduled_matches_count"], 1)

        response = self.client.post(
            f"/api/competition-categories/{self.competition_category.id}/delete-ladder/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["deleted_matches"], 1)
        self.assertEqual(response.data["deleted_scheduled_matches"], 1)
        self.assertFalse(Match.objects.filter(competition_category=self.competition_category).exists())
        self.assertFalse(Standing.objects.filter(competition_category=self.competition_category).exists())
        self.assertTrue(Competition.objects.filter(pk=self.competition.pk).exists())
        self.assertTrue(CompetitionCategory.objects.filter(pk=self.competition_category.pk).exists())
        self.assertEqual(
            Registration.objects.filter(pk__in=[item.pk for item in registrations]).count(),
            2,
        )
        self.assertEqual(Player.objects.filter(pk__in=[player.pk for player in self.players[:2]]).count(), 2)
        self.assertTrue(Court.objects.filter(pk=court.pk).exists())

        regenerate = self.client.post(
            f"/api/competition-categories/{self.competition_category.id}/generate-ladder/"
        )
        self.assertEqual(regenerate.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Match.objects.filter(competition_category=self.competition_category).count(), 1)
        self.assertEqual(Standing.objects.filter(competition_category=self.competition_category).count(), 2)

    def test_organizer_can_delete_clean_ladder_and_player_cannot(self):
        self.register(self.players[0])
        self.register(self.players[1])
        LadderService.generate_ladder(self.competition_category)
        url = f"/api/competition-categories/{self.competition_category.id}/delete-ladder/"

        self.client.force_authenticate(self.players[0].user)
        self.assertEqual(self.client.post(url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Match.objects.filter(competition_category=self.competition_category).exists())

        self.client.force_authenticate(self.organizer)
        self.assertEqual(self.client.post(url).status_code, status.HTTP_200_OK)

    def test_delete_ladder_rejects_direct_elimination_and_missing_ladder(self):
        self.client.force_authenticate(self.admin)
        missing_url = f"/api/competition-categories/{self.competition_category.id}/delete-ladder/"
        missing = self.client.post(missing_url)
        self.assertEqual(missing.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no ha sido generada", str(missing.data).lower())

        direct = self.make_competition("Directa para eliminación", "ELIMINACION_DIRECTA")
        direct_category = CompetitionCategory.objects.create(
            competition=direct,
            category=self.category,
            max_players=8,
            minimum_players=2,
        )
        response = self.client.post(
            f"/api/competition-categories/{direct_category.id}/delete-ladder/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no pertenece a una escalerilla", str(response.data).lower())

    def test_delete_ladder_blocks_every_evidence_of_sporting_activity(self):
        scenarios = (
            "match_set",
            "in_progress",
            "walkover",
            "retirement",
            "finished",
            "winner",
            "cancelled",
        )
        self.client.force_authenticate(self.admin)

        for index, scenario in enumerate(scenarios, start=1):
            competition = self.make_competition(f"Escalerilla bloqueada {scenario}")
            category = CompetitionCategory.objects.create(
                competition=competition,
                category=self.category,
                max_players=8,
                minimum_players=2,
            )
            match = Match.objects.create(
                competition_category=category,
                player1=self.players[0],
                player2=self.players[1],
            )
            Standing.objects.create(competition_category=category, player=self.players[0])

            if scenario == "match_set":
                MatchSet.objects.create(
                    match=match,
                    set_number=1,
                    games_player1=1,
                    games_player2=0,
                    is_incomplete=True,
                )
            elif scenario == "in_progress":
                match.status = Match.Status.EN_JUEGO
            elif scenario == "walkover":
                match.status = Match.Status.FINALIZADO
                match.resolution_type = Match.ResolutionType.WALKOVER
                match.is_walkover = True
                match.winner_player = self.players[0]
            elif scenario == "retirement":
                match.status = Match.Status.FINALIZADO
                match.resolution_type = Match.ResolutionType.RETIREMENT
                match.winner_player = self.players[0]
            elif scenario == "finished":
                match.status = Match.Status.FINALIZADO
            elif scenario == "winner":
                match.winner_player = self.players[0]
            elif scenario == "cancelled":
                match.status = Match.Status.CANCELADO
            match.save()

            detail = self.client.get(
                f"/api/competition-categories/{category.id}/ladder/"
            )
            self.assertFalse(detail.data["can_delete"], scenario)
            self.assertIn("partidos disputados", detail.data["delete_block_reason"], scenario)

            response = self.client.post(
                f"/api/competition-categories/{category.id}/delete-ladder/"
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, scenario)
            self.assertTrue(Match.objects.filter(pk=match.pk).exists(), scenario)
            self.assertTrue(
                Standing.objects.filter(competition_category=category).exists(),
                scenario,
            )

    def test_match_set_is_deleted_by_match_cascade(self):
        match = Match.objects.create(
            competition_category=self.competition_category,
            player1=self.players[0],
            player2=self.players[1],
        )
        match_set = MatchSet.objects.create(
            match=match,
            set_number=1,
            games_player1=1,
            games_player2=0,
            is_incomplete=True,
        )

        match.delete()

        self.assertFalse(MatchSet.objects.filter(pk=match_set.pk).exists())

    def test_normal_scoring_two_zero_and_idempotent_recalculation(self):
        self.register(self.players[0])
        self.register(self.players[1])
        match = Match.objects.create(
            competition_category=self.competition_category,
            player1=self.players[0], player2=self.players[1],
            winner_player=self.players[0], status=Match.Status.FINALIZADO,
        )
        MatchSet.objects.create(match=match, set_number=1, games_player1=6, games_player2=4)
        MatchSet.objects.create(match=match, set_number=2, games_player1=6, games_player2=2)
        LadderService.recalculate_standings(self.competition_category)
        LadderService.recalculate_standings(self.competition_category)
        winner = Standing.objects.get(player=self.players[0], competition_category=self.competition_category)
        loser = Standing.objects.get(player=self.players[1], competition_category=self.competition_category)
        self.assertEqual(
            (winner.matches_played, winner.matches_won, winner.sets_won, winner.games_won, winner.games_lost, winner.points),
            (1, 1, 2, 12, 6, 4),
        )
        self.assertEqual(
            (loser.matches_played, loser.matches_lost, loser.sets_lost, loser.games_won, loser.games_lost, loser.points),
            (1, 1, 2, 6, 12, 1),
        )

    def test_normal_two_one_excludes_super_tie_break_points_from_games(self):
        self.register(self.players[0])
        self.register(self.players[1])
        match = Match.objects.create(
            competition_category=self.competition_category,
            player1=self.players[0], player2=self.players[1],
            winner_player=self.players[0], status=Match.Status.FINALIZADO,
        )
        MatchSet.objects.create(match=match, set_number=1, games_player1=6, games_player2=4)
        MatchSet.objects.create(match=match, set_number=2, games_player1=4, games_player2=6)
        MatchSet.objects.create(match=match, set_number=3, games_player1=10, games_player2=8, is_super_tie_break=True)
        LadderService.recalculate_standings(self.competition_category)
        winner = Standing.objects.get(player=self.players[0], competition_category=self.competition_category)
        loser = Standing.objects.get(player=self.players[1], competition_category=self.competition_category)
        self.assertEqual((winner.points, loser.points), (3, 2))
        self.assertEqual((winner.sets_won, winner.sets_lost), (2, 1))
        self.assertEqual((winner.games_won, winner.games_lost), (10, 10))

    def test_walkover_and_retirement_rules(self):
        for player in self.players[:4]:
            self.register(player)
        walkover = Match.objects.create(
            competition_category=self.competition_category,
            player1=self.players[0], player2=self.players[1],
            winner_player=self.players[0], status=Match.Status.FINALIZADO,
            resolution_type=Match.ResolutionType.WALKOVER, is_walkover=True,
        )
        retirement = Match.objects.create(
            competition_category=self.competition_category,
            player1=self.players[2], player2=self.players[3],
            winner_player=self.players[2], status=Match.Status.FINALIZADO,
            resolution_type=Match.ResolutionType.RETIREMENT,
        )
        MatchSet.objects.create(match=retirement, set_number=1, games_player1=6, games_player2=4)
        MatchSet.objects.create(match=retirement, set_number=2, games_player1=2, games_player2=1, is_incomplete=True)
        LadderService.recalculate_standings(self.competition_category)
        wo_winner = Standing.objects.get(player=self.players[0], competition_category=self.competition_category)
        wo_loser = Standing.objects.get(player=self.players[1], competition_category=self.competition_category)
        self.assertEqual((wo_winner.points, wo_winner.sets_won, wo_winner.games_won, wo_winner.walkovers_won), (4, 2, 12, 1))
        self.assertEqual((wo_loser.points, wo_loser.sets_lost, wo_loser.games_lost, wo_loser.walkovers_lost), (1, 2, 12, 1))
        ret_winner = Standing.objects.get(player=self.players[2], competition_category=self.competition_category)
        ret_loser = Standing.objects.get(player=self.players[3], competition_category=self.competition_category)
        self.assertEqual((ret_winner.points, ret_winner.sets_won, ret_winner.games_won, ret_winner.games_lost), (4, 1, 8, 5))
        self.assertEqual((ret_loser.points, ret_loser.sets_lost, ret_loser.games_won, ret_loser.games_lost), (1, 1, 5, 8))
        self.assertFalse(walkover.sets.exists())

    def test_order_uses_points_set_difference_game_difference_and_wins(self):
        for player in self.players[:4]:
            self.register(player)
        LadderService.recalculate_standings(self.competition_category)
        standings = list(Standing.objects.filter(
            competition_category=self.competition_category
        ).select_related("player"))
        values = [
            (5, 3, 1, 20, 10, 1),
            (5, 3, 1, 18, 10, 4),
            (5, 2, 1, 30, 10, 5),
            (4, 9, 0, 50, 0, 9),
        ]
        for standing, value in zip(standings, values):
            (
                standing.points, standing.sets_won, standing.sets_lost,
                standing.games_won, standing.games_lost, standing.matches_won,
            ) = value
            standing.save()
        expected = [
            standing.player_id
            for standing in sorted(
                standings,
                key=LadderService.standing_sort_key,
            )
        ]
        self.assertEqual(expected, [standings[0].player_id, standings[1].player_id,
                                    standings[2].player_id, standings[3].player_id])

    def test_ladder_and_standing_security(self):
        confirmed = self.players[0]
        pending = self.players[1]
        self.register(confirmed)
        self.register(pending, "PENDIENTE")
        Standing.objects.create(competition_category=self.competition_category, player=confirmed)
        ladder_url = f"/api/competition-categories/{self.competition_category.id}/ladder/"
        generate_url = f"/api/competition-categories/{self.competition_category.id}/generate-ladder/"

        self.client.force_authenticate(confirmed.user)
        self.assertEqual(self.client.get(ladder_url).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(generate_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get("/api/standings/").data[0]["player"], confirmed.id)

        self.client.force_authenticate(pending.user)
        self.assertEqual(self.client.get(ladder_url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get("/api/standings/").data, [])

        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.get(ladder_url).status_code, status.HTTP_200_OK)
