from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reserva

class PagoForm(forms.Form):
    numero = forms.CharField(max_length=16, label="Número de tarjeta")
    titular = forms.CharField(max_length=100, label="Titular de la tarjeta")
    codigo = forms.CharField(max_length=4, label="Código de seguridad")


HORAS_CHOICES = [(f"{h:02}:00", f"{h:02}:00") for h in range(0, 24)]


class ReservaNormalForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin', 'metodo_pago']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'metodo_pago': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.inmueble = kwargs.pop('inmueble', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        inicio = cleaned_data.get("fecha_inicio")
        fin = cleaned_data.get("fecha_fin")

        if not inicio or not fin:
            return cleaned_data

        if fin <= inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")

        if (fin - inicio).days > 30:
            raise ValidationError("La duración máxima de una reserva es de 30 días.")

        if self.inmueble:
            conflictos = Reserva.objects.filter(
                inmueble=self.inmueble,
                fecha_inicio__lt=fin,
                fecha_fin__gt=inicio,
                estado="aceptada"
            )
            if self.instance.pk:
                conflictos = conflictos.exclude(pk=self.instance.pk)
            if conflictos.exists():
                raise ValidationError("Ya existe una reserva aceptada que se superpone con este rango.")

        return cleaned_data


class ReservaCocheraForm(forms.ModelForm):
    dia = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Día de reserva"
    )
    hora_inicio = forms.ChoiceField(
        choices=HORAS_CHOICES,
        label="Hora de inicio"
    )
    horas = forms.IntegerField(
        min_value=1,
        max_value=24,
        label="Duración (horas)"
    )

    class Meta:
        model = Reserva
        fields = ['metodo_pago']

    def __init__(self, *args, **kwargs):
        self.inmueble = kwargs.pop('inmueble', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get("dia")
        hora_inicio_str = cleaned_data.get("hora_inicio")
        horas = cleaned_data.get("horas")

        if not dia or not hora_inicio_str or not horas:
            raise ValidationError("Complete todos los campos de día, hora y duración.")

        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
        fecha_inicio = datetime.combine(dia, hora_inicio)
        fecha_fin = fecha_inicio + timedelta(hours=horas)

        cleaned_data["fecha_inicio"] = fecha_inicio
        cleaned_data["fecha_fin"] = fecha_fin

        if self.inmueble:
            conflictos = Reserva.objects.filter(
                inmueble=self.inmueble,
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
                estado="aceptada"
            )
            if self.instance.pk:
                conflictos = conflictos.exclude(pk=self.instance.pk)
            if conflictos.exists():
                raise ValidationError("Ya hay una reserva que se superpone con ese horario.")

        return cleaned_data

    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.fecha_inicio = self.cleaned_data["fecha_inicio"]
        instancia.fecha_fin = self.cleaned_data["fecha_fin"]
        if commit:
            instancia.save()
        return instancia