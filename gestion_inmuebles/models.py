
from django.db import models

class Inmueble(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(default='Casa', choices=[
        ('Casa', 'Casa'),
        ('Departamento', 'Departamento'),
        ('Local', 'Local'),
        ('Otro', 'Otro'),
    ]) 
    politica_cancelacion = models.TextField(blank=True)
    estado = models.CharField(default='Disponible', choices=[
        ('Disponible', 'Disponible'),
        ('No_disponible', 'No disponible'),
        ('Mantenimiento', 'En mantenimiento'),
    ])
    Precio = models.DecimalField(max_digits=10, decimal_places=2)
    Tiempo = models.CharField(default='-', choices=[
        ('Por_hora', 'Por hora'),
        ('Por_dia', 'Por día'),
        ('Por_semana', 'Por semana'),
        ('Por_mes', 'Por mes'),
        ('Por_noche', 'Por noche'),
    ]
    )
    imagen = models.ImageField(upload_to='inmuebles/', blank=True, null=True)
    superficie = models.IntegerField(default=0) 


class InmueblesSimilares(Inmueble):
    tiene_internet = models.BooleanField(default=False)
    baños = models.IntegerField(default=0) 
    tiene_cochera = models.BooleanField(default=False)
    




class Departamento(InmueblesSimilares):
    piso = models.IntegerField(null=True, blank=True)
    cantidad_inquilinos = models.IntegerField(default=1)    

class Casa(InmueblesSimilares):
    pisos = models.IntegerField(null=True, blank=True)
    cantidad_inquilinos = models.IntegerField(default=1)    

class Local(InmueblesSimilares):
    frente = models.DecimalField(max_digits=10, decimal_places=2)
    fondo = models.DecimalField(max_digits=10, decimal_places=2)

class Cochera(Inmueble):
    tipo_cochera = models.CharField(default='-', choices=[
        ('Cubierta', 'Cubierta'),
        ('Descubierta', 'Descubierta'),
    ]
    )
    largo_plaza = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ancho_plaza = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    plazas = models.IntegerField(null=True, blank=True)
    

    def __str__(self):
    
        return f"{self.nombre} - ${self.precio}"
    

