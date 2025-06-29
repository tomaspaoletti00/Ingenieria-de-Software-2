from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_estadisticas, name='menu-estadisticas'),
    path('ingresos/mensuales', views.ingresos_mensuales, name='ingresos-mensuales'),
    path('ingresos/inmuebles', views.ingresos_por_inmueble, name='ingresos-inmueble'),
]