from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reserva
from datetime import datetime, timedelta, date

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

        if isinstance(inicio, datetime):
            inicio = inicio.date()
        if isinstance(fin, datetime):
            fin = fin.date()

        ayer = date.today() - timedelta(days=1)

        if inicio <= ayer:
            raise ValidationError("La fecha de inicio no puede ser en el pasado.")
        if fin <= inicio:
            raise ValidationError("La fecha de fin debe ser posterior a la de inicio.")
        if (fin - inicio).days > 28:
            raise ValidationError("La duración máxima es de 28 días.")

        inicio_dt = datetime.combine(inicio, datetime.min.time())
        fin_dt = datetime.combine(fin, datetime.min.time())

        if self.inmueble:
            conflictos = Reserva.objects.filter(
                inmueble=self.inmueble,
                fecha_inicio__lt=fin_dt,
                fecha_fin__gt=inicio_dt,
                estado="aceptada"
            )
            if self.instance.pk:
                conflictos = conflictos.exclude(pk=self.instance.pk)
            if conflictos.exists():
                raise ValidationError("Ya hay una reserva aceptada en ese rango.")

        cleaned_data["fecha_inicio"] = inicio_dt
        cleaned_data["fecha_fin"] = fin_dt
        return cleaned_data
    
    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.fecha_inicio = self.cleaned_data["fecha_inicio"]
        instancia.fecha_fin = self.cleaned_data["fecha_fin"]
        if commit:
            instancia.save()
        return instancia


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
            raise ValidationError("Complete día, hora y duración.")

        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
        fecha_inicio = datetime.combine(dia, hora_inicio)
        fecha_fin = fecha_inicio + timedelta(hours=horas)

        ayer = date.today() - timedelta(days=1)

        if dia <= ayer:
            raise ValidationError("La fecha de reserva no puede estar en el pasado.")
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la de inicio.")

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
                raise ValidationError("Ya hay una reserva aceptada para ese horario.")

        return cleaned_data

    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.fecha_inicio = self.cleaned_data["fecha_inicio"]
        instancia.fecha_fin = self.cleaned_data["fecha_fin"]
        if commit:
            instancia.save()
        return instancia