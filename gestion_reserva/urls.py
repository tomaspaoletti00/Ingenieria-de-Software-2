from django.urls import path
from . import views

urlpatterns = [
    path('hacer_reserva/<int:id_inmueble>', views.hacer_reserva, name="hacer_reserva"),
    path('reservas/', views.listar_reservas, name='listar_reservas'),
    path('reservas/<int:reserva_id>/cambiar-estado/', views.cambiar_estado_reserva, name='cambiar_estado_reserva'),
    path('inmueble/<int:pk>/', views.inmueble_detalle, name='inmueble_detalle'),
    path('reserva/cancelar/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('reserva/pagar/<int:reserva_id>/', views.pagar_reserva, name='pagar_reserva'),
    path('reservas/horas_ocupadas/<int:inmueble_id>/', views.obtener_horas_ocupadas, name='obtener_horas_ocupadas'),

    path('agregarInquilino/<int:reserva_id>/', views.agregarInquilinos, name='insertar_inquilino'),
    path('admin/cancelar_reserva/<int:reserva_id>/', views.cancelar_reserva_admin, name='cancelar_reserva_admin'),
    path('reservas/<int:reserva_id>/actualizar/', views.actualizar_estado_dinamico, name='actualizar_estado_reserva'),

]