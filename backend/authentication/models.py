from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema de gestión
    de torneos de tenis.
    """

    pass