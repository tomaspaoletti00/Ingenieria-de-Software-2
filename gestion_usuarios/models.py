from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

class Usuario(AbstractUser):
    dni = models.CharField(max_length=10, unique=True)
    telefono = models.CharField(max_length=20)
    
    def __str__(self):
        return self.email



class TokenVerificacion(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)

    def expirado(self):
        return timezone.now() > self.creado_en + timedelta(minutes=5)