
from django.db import models

class Inmueble(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(max_length=50, choices=[
        ('casa', 'Casa'),
        ('departamento', 'Departamento'),
        ('local', 'Local'),
        ('otro', 'Otro'),
    ])
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('no_disponible', 'No disponible'),
        ('mantenimiento', 'En mantenimiento'),
    ]
    piso = models.IntegerField(null=True, blank=True)
    pisos = models.IntegerField(null=True, blank=True)
    cantidad_inquilinos = models.IntegerField()
    posee_cochera = models.BooleanField(default=False)
    habitaciones = models.IntegerField()
    banios = models.IntegerField()
    tiene_internet = models.BooleanField(default=False)
    politica_cancelacion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='inmuebles/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
    

