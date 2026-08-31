from datetime import timedelta

from django.db.models import Q

from core.models import Match


class MatchSchedulingService:
    """Consultas de disponibilidad para una reserva fija de partido."""

    MATCH_DURATION_MINUTES = 90
    MATCH_DURATION = timedelta(minutes=MATCH_DURATION_MINUTES)

    @classmethod
    def overlapping_matches(cls, scheduled_date_time, match=None):
        """Partidos cuyo intervalo se cruza con el nuevo intervalo semiabierto."""

        new_end = scheduled_date_time + cls.MATCH_DURATION
        earliest_overlapping_start = scheduled_date_time - cls.MATCH_DURATION

        matches = Match.objects.filter(
            scheduled_date_time__lt=new_end,
            scheduled_date_time__gt=earliest_overlapping_start,
        ).exclude(status=Match.Status.CANCELADO)

        if match is not None and match.pk is not None:
            matches = matches.exclude(pk=match.pk)

        return matches

    @classmethod
    def has_court_conflict(cls, scheduled_date_time, court, match=None):
        return cls.overlapping_matches(
            scheduled_date_time,
            match,
        ).filter(court=court).exists()

    @classmethod
    def has_player_conflict(
        cls,
        scheduled_date_time,
        player1,
        player2,
        match=None,
    ):
        player_ids = [player.id for player in (player1, player2) if player is not None]

        if not player_ids:
            return False

        return cls.overlapping_matches(
            scheduled_date_time,
            match,
        ).filter(
            Q(player1_id__in=player_ids)
            | Q(player2_id__in=player_ids)
        ).exists()
