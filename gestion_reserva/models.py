from django.db import models


class Reserva(models.Model):
    
    METODOS_PAGO = [
        #('efectivo', 'Efectivo'),
        # ('transferencia', 'Transferencia'),
        #('mercado_pago', 'Mercado_pago'),
        ('tarjeta', 'Tarjeta de crédito'),
    ]
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('pendiente_pago', 'Pendiente de pago'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
    ]
    

    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    usuario = models.ForeignKey('gestion_usuarios.Usuario', on_delete=models.CASCADE)
    inmueble = models.ForeignKey('gestion_inmuebles.Inmueble', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default="efectivo")
   
    datos_inquilinos = models.JSONField()


class Tarjeta(models.Model):
    numero = models.CharField(max_length=16)
    titular = models.CharField(max_length=100)
    codigo = models.CharField(max_length=4)
    monto_disponible = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return f"{self.titular} - {self.numero}"

