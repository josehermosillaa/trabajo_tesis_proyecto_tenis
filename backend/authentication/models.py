from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    """
    Representa un rol de usuario dentro del sistema.
    """

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema de gestión
    de torneos de tenis.
    """

    role = models.ForeignKey(
    Role,
    on_delete=models.PROTECT,
    related_name="users"
)