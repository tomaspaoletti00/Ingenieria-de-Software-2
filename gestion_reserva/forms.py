from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from .models import Reserva
from django.contrib import admin
from .models import Tarjeta


class PagoForm(forms.Form):
    numero = forms.CharField(max_length=16, label="Número de tarjeta")
    titular = forms.CharField(max_length=100, label="Titular de la tarjeta")
    codigo = forms.CharField(max_length=4, label="Código de seguridad")

class ReservaNormalForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin', 'metodo_pago']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'metodo_pago': forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if not fecha_inicio or not fecha_fin:
            return

        if fecha_fin <= fecha_inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

        if (fecha_fin - fecha_inicio).days > 31:
            raise ValidationError("La duración mínima de una reserva normal debe ser de al menos un mes.")

        inmueble = self.initial.get("inmueble")
        if not inmueble:
            return

        conflictos = Reserva.objects.filter(
            inmueble=inmueble,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio,
            estado="aceptada"
        )
        if self.instance.pk:
            conflictos = conflictos.exclude(pk=self.instance.pk)

        if conflictos.exists():
            raise ValidationError("El inmueble ya está reservado en el rango de fechas seleccionado.")

    def save(self, commit=True):
        instancia = super().save(commit=False)
        if commit:
            instancia.save()
        return instancia

from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reserva

from django import forms
from datetime import time

HORAS_CHOICES = [(f"{h:02}:00", f"{h:02}:00") for h in range(0, 24)]

class ReservaCocheraForm(forms.ModelForm):
    dia = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Día"
    )
    hora_inicio = forms.ChoiceField(
        choices=HORAS_CHOICES,
        label="Hora de inicio"
    )
    horas = forms.IntegerField(
        min_value=1,
        max_value=24,
        label="Cantidad de horas"
    )

    class Meta:
        model = Reserva
        fields = ['metodo_pago']

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get("dia")
        hora_inicio_str = cleaned_data.get("hora_inicio")
        horas = cleaned_data.get("horas")

        if not dia or not hora_inicio_str or not horas:
            raise ValidationError("Debe completar el día, la hora de inicio y la cantidad de horas.")

        # Convertir el string "HH:00" a objeto time
        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()

        fecha_inicio = datetime.combine(dia, hora_inicio)
        fecha_fin = fecha_inicio + timedelta(hours=horas)

        cleaned_data["fecha_inicio"] = fecha_inicio
        cleaned_data["fecha_fin"] = fecha_fin

        inmueble = self.initial.get("inmueble")
        if not inmueble:
            return

        conflictos = Reserva.objects.filter(
            inmueble=inmueble,
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        )
        if self.instance.pk:
            conflictos = conflictos.exclude(pk=self.instance.pk)

        if conflictos.exists():
            raise ValidationError("La cochera ya está reservada en ese horario.")

    def save(self, commit=True):
        instancia = super().save(commit=False)
        cleaned_data = self.cleaned_data
        instancia.fecha_inicio = cleaned_data["fecha_inicio"]
        instancia.fecha_fin = cleaned_data["fecha_fin"]
        if commit:
            instancia.save()
        return instancia
