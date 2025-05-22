from django.urls import path
from . import views

urlpatterns = [
    path('hacer_reserva/<int:id_inmueble>', views.hacer_reserva, name="hacer_reserva"),
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('reservas/<int:reserva_id>/cambiar-estado/', views.cambiar_estado_reserva, name='cambiar_estado_reserva'),
]