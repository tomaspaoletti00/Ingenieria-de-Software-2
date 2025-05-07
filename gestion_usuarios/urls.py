from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('registro/', views.registrar_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_usuario, name='logout'),
    
]