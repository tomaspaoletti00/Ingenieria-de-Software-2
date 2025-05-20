from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta

class Reserva(models.Model):
    TIPO_RESERVA = [
        ('normal', 'Normal'),
        ('cochera', 'Cochera'),
    ]

    usuario = models.ForeignKey('gestion_usuarios.Usuario', on_delete=models.CASCADE)
    inmueble = models.ForeignKey('gestion_inmuebles.Inmueble', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    tipo = models.CharField(max_length=10, choices=TIPO_RESERVA)
    estado = models.CharField(max_length=20, default="pendiente")
    datos_inquilinos = models.JSONField()

    def clean(self):
        super().clean()

        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

        if self.tipo == 'normal':
            diferencia = self.fecha_fin.date() - self.fecha_inicio.date()
            if diferencia < timedelta(days=28):  # Consideramos 28 como mínimo para evitar falsos positivos con febrero
                raise ValidationError("La duración mínima de una reserva normal debe ser de al menos un mes.")

            # Validación de superposición
            conflictos = Reserva.objects.filter(
                inmueble=self.inmueble,
                tipo='normal',
                fecha_inicio__lt=self.fecha_fin,
                fecha_fin__gt=self.fecha_inicio
            ).exclude(pk=self.pk)
            if conflictos.exists():
                raise ValidationError("El inmueble ya está reservado en el rango de fechas seleccionado.")
        
        elif self.tipo == 'cochera':
            # Validación más corta para cochera (horaria)
            conflictos = Reserva.objects.filter(
                inmueble=self.inmueble,
                tipo='cochera',
                fecha_inicio__lt=self.fecha_fin,
                fecha_fin__gt=self.fecha_inicio
            ).exclude(pk=self.pk)
            if conflictos.exists():
                raise ValidationError("La cochera ya está reservada en el rango horario seleccionado.")

    def __str__(self):
        return f"Reserva {self.tipo} de {self.usuario} para {self.inmueble}"