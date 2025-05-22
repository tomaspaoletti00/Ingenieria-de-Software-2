from django.db import models

from django.db import models

class Reserva(models.Model):
    METODOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('mercado_pago', 'Mercado Pago'),
        ('tarjeta', 'Tarjeta de crédito/débito'),
    ]

    usuario = models.ForeignKey('gestion_usuarios.Usuario', on_delete=models.CASCADE)
    inmueble = models.ForeignKey('gestion_inmuebles.Inmueble', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default="efectivo")
    estado = models.CharField(max_length=20, default="pendiente")
    metodo_pago = models.CharField(max_length=50)
    datos_inquilinos = models.JSONField()

