from django.urls import path
from . import views

urlpatterns = [
    path('hacer_reserva/<int:id_inmueble>', views.hacer_reserva, name="hacer_reserva"),
]