from django.urls import path
from . import views


urlpatterns = [
    path('crear/', views.crear_inmueble, name='crear_inmueble'),
    path('adminInmuebles/', views.adminInmuebles, name='adminInmuebles'),
    path('listaInmuebles/', views.listar_Inmuebles, name='listaInmuebles'),
    path('formularioInmueble/', views.formulario_inmueble, name='formularioInmueble'),
    path('formulario/', views.crear_formulario),
    path('inmuebles/', views.listar_Inmuebles, name='listar_Inmuebles'),
    path('inmuebles/<int:pk>/', views.inmueble_detalle, name='inmueble_detalle')
]