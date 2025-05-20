from django import forms
from django.forms import ModelForm
from .models import Reserva

class ReservaNormalForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.tipo = 'normal'
        return instancia if not commit else instancia.save()


class ReservaCocheraForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['fecha_inicio', 'fecha_fin']
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def save(self, commit=True):
        instancia = super().save(commit=False)
        instancia.tipo = 'cochera'
        return instancia if not commit else instancia.save()