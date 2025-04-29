from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_inmueble, name='crear_inmueble'),
]