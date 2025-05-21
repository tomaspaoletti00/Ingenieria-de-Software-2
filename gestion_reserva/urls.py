from django.urls import path
from . import views

urlpatterns = [
    path('prueba/', views.pagina_prueba),
    path('prueba/normal/', views.campo_reserva_normal),
    path('prueba/cochera/', views.campo_reserva_cochera),
    path('reserva/crear/', views.realizar_reserva, name="crear-reserva"),
]