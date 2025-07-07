from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Reserva
from datetime import datetime, timedelta, date
from gestion_inmuebles.models import Cochera
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
            'fecha_inicio': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'text', 'class': 'datepicker'}),
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
        if (fin - inicio).days > 30:
            raise ValidationError("La duración máxima de una reserva es de 30 días.")

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


from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date
from collections import defaultdict
from .models import Reserva
from gestion_inmuebles.models import Cochera

class ReservaCocheraForm(forms.ModelForm):
    dia = forms.DateField(
        widget=forms.DateInput(attrs={'id': 'id_dia', 'type': 'text', 'class': 'datepicker'}),
        label="Día de reserva"
    )
    hora_inicio = forms.ChoiceField(
    choices=HORAS_CHOICES,
    label="Hora de inicio",
    widget=forms.Select(attrs={'id': 'id_hora_inicio'})
    )
    hora_fin = forms.ChoiceField(
        choices=HORAS_CHOICES,
        label="Hora de fin",
        widget=forms.Select(attrs={'id': 'id_hora_fin'})
    )

    class Meta:
        model = Reserva
        fields = ['metodo_pago']

    def __init__(self, *args, **kwargs):
        self.inmueble = kwargs.pop('inmueble', None)
        super().__init__(*args, **kwargs)

        self.dias_bloqueados = []
        if self.inmueble:
            cochera = Cochera.objects.get(pk=self.inmueble.pk)
            reservas = Reserva.objects.filter(
                inmueble=self.inmueble,
                estado="aceptada"
            )

            horas_por_dia = defaultdict(lambda: defaultdict(int))
            for r in reservas:
                dia_reserva = r.fecha_inicio.date()
                h_inicio = r.fecha_inicio.hour
                h_fin = r.fecha_fin.hour
                for h in range(h_inicio, h_fin):
                    horas_por_dia[dia_reserva][h] += 1

            horas_posibles = range(0, 24)
            for dia, horas in horas_por_dia.items():
                if all(horas.get(h, 0) >= cochera.plazas for h in horas_posibles):
                    self.dias_bloqueados.append(dia.strftime("%Y-%m-%d"))

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get("dia")
        hora_inicio_str = cleaned_data.get("hora_inicio")
        hora_fin_str = cleaned_data.get("hora_fin")

        if not dia or not hora_inicio_str or not hora_fin_str:
            raise ValidationError("Complete día y rango horario.")

        hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
        hora_fin = datetime.strptime(hora_fin_str, "%H:%M").time()
        fecha_inicio = datetime.combine(dia, hora_inicio)
        fecha_fin = datetime.combine(dia, hora_fin)

        ayer = date.today() - timedelta(days=1)
        if dia <= ayer:
            raise ValidationError("La fecha no puede estar en el pasado.")
        if fecha_fin <= fecha_inicio:
            raise ValidationError("La hora de fin debe ser posterior a la de inicio.")

        cleaned_data["fecha_inicio"] = fecha_inicio
        cleaned_data["fecha_fin"] = fecha_fin

        if self.inmueble:
            cochera = Cochera.objects.get(pk=self.inmueble.pk)
            conflictos = Reserva.objects.filter(
                inmueble=self.inmueble,
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
                estado="aceptada"
            )
            if self.instance.pk:
                conflictos = conflictos.exclude(pk=self.instance.pk)

            horas_conflicto = defaultdict(int)
            for r in conflictos:
                h_inicio = r.fecha_inicio.hour
                h_fin = r.fecha_fin.hour
                for h in range(h_inicio, h_fin):
                    horas_conflicto[h] += 1

            for h in range(hora_inicio.hour, hora_fin.hour):
                if horas_conflicto.get(h, 0) >= cochera.plazas:
                    raise ValidationError("Horario ya sin plazas disponibles.")

        return cleaned_data

    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.fecha_inicio = self.cleaned_data["fecha_inicio"]
        instancia.fecha_fin = self.cleaned_data["fecha_fin"]
        if commit:
            instancia.save()
        return instancia