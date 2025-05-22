from django import forms
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from .models import Reserva

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

        if (fecha_fin.date() - fecha_inicio.date()).days < 28:
            raise ValidationError("La duración mínima de una reserva normal debe ser de al menos un mes.")

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
            raise ValidationError("El inmueble ya está reservado en el rango de fechas seleccionado.")

    def save(self, commit=True):
        instancia = super().save(commit=False)
        if commit:
            instancia.save()
        return instancia

class ReservaCocheraForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin', 'metodo_pago']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'metodo_pago': forms.Select(),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_fin = cleaned_data.get("fecha_fin")

        if not fecha_inicio or not fecha_fin:
            return

        if fecha_fin <= fecha_inicio:
            raise ValidationError("La fecha y hora de fin debe ser posterior a la de inicio.")

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
        if commit:
            instancia.save()
        return instancia
