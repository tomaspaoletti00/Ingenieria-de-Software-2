from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_estadisticas, name='menu-estadisticas'),
    path('ingresos/mensuales', views.ingresos_mensuales, name='ingresos-mensuales'),
    path('ingresos/inmuebles', views.ingresos_por_inmueble, name='ingresos-inmueble'),
    path('ingresos/tipo', views.ingresos_por_tipo, name='ingresos-tipo'),
    path('porcentaje/tipo', views.porcentaje_reservas_por_tipo, name='porcentaje-tipo'),
    path('porcentaje/total', views.total_ingresos, name='ingresos-total'),
    path('ingresos/diarios', views.estadistica_ingresos_diario, name='ingresos-diarios'),

]