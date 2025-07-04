from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('registro/', views.registrar_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_usuario, name='logout'),
    path('panel-emp', views.panelEmp, name='panel-emp'),
    path('panel-admin', views.panelAdmin, name='panel-admin'),
    path('panel-emp/lista-clientes/', views.listar_clientes, name='lista-clientes'),
    path('panel-emp/lista-clientes/<int:user_id>/', views.detalle_cliente, name='detalle-cliente'),
    path('perfil/', views.ver_perfil, name='perfil_usuario'),
    path('perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('panel-admin/lista-empleados/', views.listar_empleados, name='lista-empleados'),
    path('panel-admin/lista-empleados/<int:user_id>/', views.detalle_empleado, name='detalle-empleado'),
    path('verificar-token/', views.verificar_token, name='verificar-token'),
    path('verificar-token/reenviar/', views.reenviar_token, name='reenviar-token'),
    path('panel-admin/alta-empleado/', views.alta_empleado, name='alta_empleado'),
    path('baja-empleado/<int:user_id>/', views.baja_empleado, name='baja_empleado'),
    path('editar-empleado/<int:user_id>/', views.editar_empleado, name='editar-empleado'),
    path('panel-admin/alta-empleado/', views.alta_empleado, name='alta_empleado'),
    path('deshabilitar/<int:user_id>/', views.deshabilitar_usuario, name='deshabilitar_usuario'),
    path('usuarios/habilitar/<int:user_id>/', views.habilitar_usuario, name='habilitar_usuario'),
    path('empleados/<int:user_id>/habilitar/', views.habilitar_empleado, name='habilitar_empleado'),
    path('alta-manual/', views.alta_manual_usuario, name= 'alta-manual')



]