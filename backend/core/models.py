
from django.conf import settings
from django.db import models

class Player(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="player"
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