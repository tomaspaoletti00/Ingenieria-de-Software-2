from django import forms
from django.forms import ModelForm, Form
from .models import Reserva, ReservaNormal, ReservaCochera

class CampoReservaNormal(ModelForm):
    class Meta:
        model = ReservaNormal
        fields = ['fecha_inicio', 'fecha_fin']

class CampoReservaCochera(ModelForm):
    class Meta:
        model = ReservaCochera
        fields = ['hora_inicio', 'hora_fin']

class CampoReservaPago(ModelForm):
    class Meta:
        model = Reserva
        fields = ['metodo_pago']