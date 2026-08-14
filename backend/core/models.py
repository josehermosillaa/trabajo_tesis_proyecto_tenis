
from django.conf import settings
from django.db import models


class Player(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="player"
    )

    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="players"
    )

    rut = models.CharField(
        max_length=12,
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    birth_date = models.DateField(
        null=True,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Competition(models.Model):

    name = models.CharField(max_length=150)

    type = models.CharField(
        max_length=30,
        choices=[
            ("ESCALERILLA", "Escalerilla"),
            ("ELIMINACION_DIRECTA", "Eliminación directa"),
        ]
    )

    start_date = models.DateField()

    end_date = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDIENTE", "Pendiente"),
            ("ABIERTA", "Abierta"),
            ("EN_CURSO", "En curso"),
            ("FINALIZADA", "Finalizada"),
            ("CANCELADA", "Cancelada"),
        ],
        default="PENDIENTE"
    )

    registration_deadline = models.DateField()

    def __str__(self):
        return self.name
    
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
class CompetitionCategory(models.Model):
    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name="competition_categories",
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="competition_categories",
    )

    max_players = models.PositiveIntegerField()
    minimum_players = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["competition", "category"],
                name="unique_competition_category",
            )
        ]

    def __str__(self):
        return f"{self.competition.name} - {self.category.name}"
    
class Registration(models.Model):
    competition_category = models.ForeignKey(
        CompetitionCategory,
        on_delete=models.CASCADE,
        related_name="registrations",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="registrations",
    )

    registration_date = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDIENTE", "Pendiente"),
            ("CONFIRMADA", "Confirmada"),
            ("CANCELADA", "Cancelada"),
        ],
        default="PENDIENTE",
    )

    seed = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "player",
                    "competition_category",
                ],
                name="unique_player_competition_category",
            )
        ]

    def __str__(self):
        return (
            f"{self.player} - "
            f"{self.competition_category}"
        )
        
        
        
class Match(models.Model):

    class Status(models.TextChoices):
        PROGRAMADO = "PROGRAMADO", "Programado"
        EN_JUEGO = "EN_JUEGO", "En juego"
        FINALIZADO = "FINALIZADO", "Finalizado"
        CANCELADO = "CANCELADO", "Cancelado"

    competition_category = models.ForeignKey(
        CompetitionCategory,
        on_delete=models.CASCADE,
        related_name="matches",
    )

    court = models.ForeignKey(
        "Court",
        on_delete=models.PROTECT,
        related_name="matches",
        null=True,
        blank=True,
    )

    player1 = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="matches_as_player1",
    )

    player2 = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="matches_as_player2",
        null=True,
        blank=True,
    )

    winner_player = models.ForeignKey(
        Player,
        on_delete=models.PROTECT,
        related_name="matches_won",
        null=True,
        blank=True,
    )

    scheduled_date_time = models.DateTimeField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PROGRAMADO,
    )

    round = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_walkover = models.BooleanField(
        default=False,
    )
class Court(models.Model):

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Disponible"
        OCCUPIED = "OCCUPIED", "Ocupada"
        MAINTENANCE = "MAINTENANCE", "Mantención"

    name = models.CharField(
        max_length=100,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )

    def __str__(self):
        return self.name
    
class MatchSet(models.Model):

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name="sets",
    )

    set_number = models.PositiveIntegerField()

    games_player1 = models.PositiveIntegerField()

    games_player2 = models.PositiveIntegerField()

    is_super_tie_break = models.BooleanField(
        default=False,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["match", "set_number"],
                name="unique_match_set_number",
            )
        ]

    def __str__(self):
        return (
            f"{self.match} - Set {self.set_number}"
        )
        


class Standing(models.Model):

    competition_category = models.ForeignKey(
        CompetitionCategory,
        on_delete=models.CASCADE,
        related_name="standings",
    )

    player = models.ForeignKey(
        Player,
        on_delete=models.CASCADE,
        related_name="standings",
    )

    matches_played = models.PositiveIntegerField(
        default=0,
    )

    matches_won = models.PositiveIntegerField(
        default=0,
    )

    matches_lost = models.PositiveIntegerField(
        default=0,
    )

    walkovers_won = models.PositiveIntegerField(
        default=0,
    )

    walkovers_lost = models.PositiveIntegerField(
        default=0,
    )

    sets_won = models.PositiveIntegerField(
        default=0,
    )

    sets_lost = models.PositiveIntegerField(
        default=0,
    )

    games_won = models.PositiveIntegerField(
        default=0,
    )

    games_lost = models.PositiveIntegerField(
        default=0,
    )

    points = models.PositiveIntegerField(
        default=0,
    )

    position = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "competition_category",
                    "player",
                ],
                name="unique_standing_player_competition_category",
            )
        ]

    def __str__(self):
        return (
            f"{self.player} - "
            f"{self.competition_category}"
        )
        
class AuditLog(models.Model):

    ACTION_CHOICES = [
        ("CREATE", "Crear"),
        ("UPDATE", "Actualizar"),
        ("DELETE", "Eliminar"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )

    username = models.CharField(
        max_length=150,
    )

    user_name = models.CharField(
        max_length=200,
    )

    entity_name = models.CharField(
        max_length=100,
    )

    entity_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.action} - "
            f"{self.entity_name} - "
            f"{self.entity_id}"
        )