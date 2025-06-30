from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_estadisticas, name='menu-estadisticas'),
    path('ingresos/', views.ingresos_mensuales, name='ingresos-mensuales'),
]