import json
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReservaNormalForm, ReservaCocheraForm
from gestion_inmuebles.models import Inmueble, Casa, Departamento
from django.http import JsonResponse
from .models import Reserva,Tarjeta
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.contrib import messages
from .forms import  PagoForm
from django.http import HttpResponseForbidden
from decimal import Decimal
from gestion_reserva.models import Tarjeta

from django.shortcuts import render

def obtener_cant_inquilino(tipo_inmueble, id_inmueble):
    if tipo_inmueble == "Casa":
        return Casa.objects.get(pk=id_inmueble).cantidad_inquilinos
    elif tipo_inmueble == "Departamento":
        return Departamento.objects.get(pk=id_inmueble).cantidad_inquilinos
    return 1


@login_required
def hacer_reserva(request, id_inmueble):
    inmueble = get_object_or_404(Inmueble, pk=id_inmueble)
    tipo_inmueble = inmueble.tipo
    cant_inquilino = obtener_cant_inquilino(tipo_inmueble, inmueble.id)

    FormClase = ReservaCocheraForm if tipo_inmueble == "Cochera" else ReservaNormalForm

    if request.method == "POST":
        form = FormClase(request.POST, inmueble=inmueble)

        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.inmueble = inmueble

            try:
                datos_inquilinos = json.loads(request.POST.get("datos_inquilinos", "[]"))
                if not datos_inquilinos:
                    form.add_error(None, "Debe agregar al menos una persona.")
                else:
                    reserva.datos_inquilinos = datos_inquilinos
                    reserva.save()
                    return redirect("inmueble_detalle", pk=inmueble.id)
            except json.JSONDecodeError:
                form.add_error(None, "Error al procesar los datos de los inquilinos.")
    else:
        form = FormClase(inmueble=inmueble)

    return render(request, "gestion_reserva/hacer_reserva.html", {
        "form": form,
        "cant_inquilino": cant_inquilino,
        "tipo_inmueble": tipo_inmueble,
        "inmueble": inmueble,
        "usuario": request.user
    })


@login_required
def listar_reservas(request):
    if request.user.is_superuser or request.user.is_staff:
        reservas = Reserva.objects.all()
        puede_cambiar_estado = True
        tarjeta = Tarjeta.objects.get(numero="5555444433331111")
        tarjeta.monto_disponible = 50000
        tarjeta.save()
        # Create your views here.
    else:
        reservas = Reserva.objects.filter(usuario=request.user)
        puede_cambiar_estado = False

    return render(request, 'gestion_reserva/listar_reservas.html', {
        'reservas': reservas,
        'puede_cambiar_estado': puede_cambiar_estado,
    })

@login_required
def cambiar_estado_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        nuevo_estado = request.POST.get('nuevo_estado')
        inmueble_id = request.POST.get('inmueble_id')

        if nuevo_estado == 'aceptada' and reserva.estado == 'pendiente':
            reserva.estado = 'pendiente_pago'
            reserva.save()
        elif nuevo_estado == 'rechazada' and reserva.estado == 'pendiente':
            reserva.estado = 'rechazada'
            reserva.save()
        return redirect('inmueble_detalle', pk=inmueble_id)

@login_required
def inmueble_detalle(request, pk):
    inmueble = get_object_or_404(Inmueble, pk=pk)
    puede_cambiar_estado = request.user.is_staff or request.user.is_superuser

    if request.user.is_staff:  # Admin o empleado
        reservas = Reserva.objects.filter(inmueble=inmueble)
        puede_cambiar_estado = True
    else:  # Usuario común
        reservas = Reserva.objects.filter(inmueble=inmueble, usuario=request.user, estado__in=['pendiente_pago', 'aceptada','pendiente'])
        puede_cambiar_estado = False

    reservas_aceptadas = reservas.filter(estado='aceptada')
    reservas_pendientes = reservas.filter(estado__in=['pendiente_pago', 'pendiente'])

    context = {
        'inmueble': inmueble,
        'reservas_aceptadas': reservas_aceptadas,
        'reservas_pendientes': reservas_pendientes,
        'puede_cambiar_estado': puede_cambiar_estado,
        'user': request.user,
        'estados_cancelables': ['pendiente', 'pendiente_pago','aceptada'],
    }
    return render(request, 'gestion_inmuebles/detalle_inmueble.html', context)

@login_required
def pagar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

    if reserva.estado != 'pendiente_pago':
        return HttpResponseForbidden("Esta reserva no se puede pagar.")

    if request.method == "POST":
        form = PagoForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero"]
            titular = form.cleaned_data["titular"]
            codigo = form.cleaned_data["codigo"]

            try:
                tarjeta = Tarjeta.objects.get(numero=numero, titular=titular, codigo=codigo)
            except Tarjeta.DoesNotExist:
                form.add_error(None, "Los datos de la tarjeta son incorrectos.")
                return render(request, "gestion_reserva/pagar_reserva.html", {"form": form, "reserva": reserva})
            
            # Suponiendo que el monto a pagar es una propiedad del inmueble
            monto_reserva = reserva.inmueble.precio

            if tarjeta.monto_disponible < monto_reserva:
                form.add_error(None, "Saldo insuficiente en la tarjeta.")
                return render(request, "gestion_reserva/pagar_reserva.html", {"form": form, "reserva": reserva})

            # Descontar y aceptar la reserva
            tarjeta.monto_disponible -= monto_reserva
            tarjeta.save()

            reserva.estado = "aceptada"
            reserva.save()

            conflictos = Reserva.objects.filter(
                inmueble=reserva.inmueble,
                estado__in=['pendiente', 'pendiente_pago'],
                fecha_inicio__lt=reserva.fecha_fin,
                fecha_fin__gt=reserva.fecha_inicio
            ).exclude(pk=reserva.pk)

            for r in conflictos:
                r.estado = 'rechazada'
                r.save()

            # Aca podrías llamar a una función para rechazar reservas en conflicto
            return redirect("inmueble_detalle", pk=reserva.inmueble.id)
    else:
        form = PagoForm()

    return render(request, "gestion_reserva/pagar_reserva.html", {"form": form, "reserva": reserva})

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

    if reserva.estado in ['pendiente', 'pendiente_pago','aceptada']:
        reserva.estado = 'cancelada'
        reserva.save()
        messages.success(request, "Reserva cancelada correctamente.")
    else:
        messages.error(request, "No se puede cancelar esta reserva.")

    return redirect('inmueble_detalle', pk=reserva.inmueble.id)