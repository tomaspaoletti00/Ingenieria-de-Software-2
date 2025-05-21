from django.urls import path
from . import views

urlpatterns = [
    path('prueba/', views.pagina_prueba, name="reserva"),
    path('prueba/normal/<int:inmueble_id>/', views.campo_reserva_normal, name="reserva-normal"),
    path('prueba/cochera/', views.campo_reserva_cochera),
    path('reserva/crear/', views.realizar_reserva, name="crear-reserva"),
    path('reserva/<int:inmueble_id>/', views.pagina_prueba, name="reserva"),
]