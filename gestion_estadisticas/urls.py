from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_estadisticas, name='menu-estadisticas'),
]