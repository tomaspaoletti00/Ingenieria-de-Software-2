from django.urls import path
from . import views

urlpatterns = [
    path('crear/', views.crear_inmueble, name='crear_inmueble'),
    path('adminInmuebles/', views.adminInmuebles, name='adminInmuebles'),
    path('listaInmuebles/', views.listarInmuebles, name='listaInmuebles'),
    path('formularioInmueble/', views.formulario_inmueble, name='formularioInmueble'),
    path('formulario/', views.crear_formulario),
]