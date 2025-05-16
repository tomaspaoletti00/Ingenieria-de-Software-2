from django.db import models

# Create your models here.
class Reserva(models.Model):
    inquilinos = models.JSONField()
    estado = models.TextField()
    inmueble = models.ForeignKey('InmueblesSimilares', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    metodo_pago = models.TextField(choices=[
        ('efectivo', 'efectivo'),
        ('transferencia bancaria', 'transferencia bancaria'),
    ])

class ReservaNormal(Reserva):
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

class ReservaCochera(Reserva):
    hora_inicio = models.DateTimeField()
    hora_fin = models.DateTimeField()