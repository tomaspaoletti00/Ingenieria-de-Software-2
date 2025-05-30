
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Inmueble(models.Model):
    activo = models.BooleanField(default=True)
    tipo = models.CharField(default='-',max_length=20, editable=False)
    nombre = models.CharField(max_length=100)
    calle = models.PositiveIntegerField(default=0)
    numero = models.PositiveIntegerField(default=0)
    provincia = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    politica_cancelacion = models.TextField(blank=True)
    estado = models.CharField(default='Disponible', choices=[
        ('Disponible', 'Disponible'),
        ('No_disponible', 'No disponible'),
        ('Mantenimiento', 'En mantenimiento'),
    ])
    precio = models.PositiveIntegerField(default=0)
    tiempo = models.CharField(default='-', choices=[
        ('Por_hora', 'Por hora'),
        ('Por_dia', 'Por día'),
        ('Por_semana', 'Por semana'),
        ('Por_mes', 'Por mes'),
        ('Por_noche', 'Por noche'),
    ]
    )
    imagen = models.ImageField(upload_to='inmuebles/', blank=True, null=True)
    superficie = models.PositiveIntegerField(default=0) 



class InmueblesSimilares(Inmueble):
    tiene_internet = models.BooleanField(default=False)
    banios = models.PositiveIntegerField(default=0) 
    tiene_cochera = models.BooleanField(default=False)
    habitaciones = models.PositiveIntegerField(default=0)
    




class Departamento(InmueblesSimilares):
    piso = models.PositiveIntegerField(null=True, blank=True)
    cantidad_inquilinos = models.PositiveIntegerField(default=1)    
    tipo = "Departamento"

    def save(self, *args, **kwargs):
        self.tipo = "Departamento"
        super().save(*args, **kwargs)

class Casa(InmueblesSimilares):
    pisos = models.PositiveIntegerField(null=True, blank=True)
    cantidad_inquilinos = models.PositiveIntegerField(default=1)    
    tipo = "Casa"

    def save(self, *args, **kwargs):
        self.tipo = "Casa"
        super().save(*args, **kwargs)


class Local(InmueblesSimilares):
    frente = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    fondo = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    tipo = "Local"

    def save(self, *args, **kwargs):
        self.tipo = "Local"
        super().save(*args, **kwargs)

class Cochera(Inmueble):
    tipo_cochera = models.CharField(default='-', choices=[
        ('Cubierta', 'Cubierta'),
        ('Descubierta', 'Descubierta'),
    ]
    )
    largo_plaza = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    ancho_plaza = models.DecimalField(max_digits=10, decimal_places=2,validators=[MinValueValidator(Decimal('0.00'))])
    plazas = models.PositiveIntegerField(null=True, blank=True)
    tipo = "Cochera"

    def save(self, *args, **kwargs):
        self.tipo = "Cochera"
        super().save(*args, **kwargs)
    

    def __str__(self):
    
        return f"{self.nombre} - ${self.precio}"
    

