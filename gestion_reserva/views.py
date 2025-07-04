import json
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReservaNormalForm, ReservaCocheraForm
from gestion_inmuebles.models import Inmueble, Casa, Departamento, Local, Cochera
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
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q

from django.shortcuts import render

from django.http import JsonResponse
from datetime import datetime
from django.shortcuts import get_object_or_404
from .models import Reserva
from gestion_inmuebles.models import Inmueble, Cochera
from collections import defaultdict

def obtener_horas_ocupadas(request, inmueble_id):
    dia_str = request.GET.get("dia")
    dia = datetime.strptime(dia_str, "%Y-%m-%d").date()

    inmueble = get_object_or_404(Inmueble, pk=inmueble_id)
    cochera = get_object_or_404(Cochera, pk=inmueble.pk)

    reservas = Reserva.objects.filter(
        inmueble=inmueble,
        estado="aceptada",
        fecha_inicio__date=dia
    )

    horas_ocupadas = defaultdict(int)
    for r in reservas:
        h_inicio = r.fecha_inicio.hour
        h_fin = r.fecha_fin.hour
        for h in range(h_inicio, h_fin):
            horas_ocupadas[h] += 1

    horas_completas = [h for h, cant in horas_ocupadas.items() if cant >= cochera.plazas]
    return JsonResponse({"horas_ocupadas": horas_completas})

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

    limite_minutos = 3
    tiempo_limite_pago = timezone.now() - timedelta(minutes=limite_minutos)

    expiradas = Reserva.objects.filter(
        estado='pendiente_pago',
        fecha_pendiente_pago__lt=tiempo_limite_pago
    )
    for res in expiradas:
        res.estado = 'cancelada'
        res.save()

    conflictos = Reserva.objects.filter(
        inmueble=inmueble
    ).filter(
        Q(estado='aceptada') | Q(estado='pendiente_pago', fecha_pendiente_pago__gte=tiempo_limite_pago)
    ).values_list('fecha_inicio', 'fecha_fin')

    fechas_ocupadas = set()
    for inicio, fin in conflictos:
        actual = inicio.date()
        while actual <= fin.date():
            fechas_ocupadas.add(actual.isoformat())
            actual += timedelta(days=1)

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
                    messages.success(request, 'Reserva exitosa.')
                    return redirect("inmueble_detalle", pk=inmueble.id)
            except json.JSONDecodeError:
                form.add_error(None, "Error al procesar los datos de los inquilinos.")
    else:
        form = FormClase(inmueble=inmueble)

    # ✅ Ahora que el form ya existe, puedo acceder a .dias_bloqueados
    dias_bloqueados = form.dias_bloqueados if tipo_inmueble == "Cochera" else []

    return render(request, "gestion_reserva/hacer_reserva.html", {
        "form": form,
        "cant_inquilino": cant_inquilino,
        "tipo_inmueble": tipo_inmueble,
        "inmueble": inmueble,
        "usuario": request.user,
        "fechas_ocupadas": list(fechas_ocupadas),
        "dias_bloqueados": dias_bloqueados,
    })



@login_required

def listar_reservas(request):
    reservas_aceptadas = Reserva.objects.filter(usuario=request.user, estado='aceptada')
    reservas_pendientes = Reserva.objects.filter(usuario=request.user,estado__in=['pendiente_pago', 'pendiente'])
    reservas_canceladas = Reserva.objects.filter(usuario=request.user, estado='cancelada')
    puede_cambiar_estado = False  # Solo para admins o empleados, si querés podés condicionar

    return render(request, 'gestion_reserva/listar_reservas.html', {
        'reservas_aceptadas': reservas_aceptadas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_canceladas': reservas_canceladas,
        'puede_cambiar_estado': puede_cambiar_estado,
        'user': request.user,  # Por si lo necesitás en la tabla
        'estados_cancelables': ['pendiente', 'pendiente_pago', 'aceptada'],
    })

from django.utils.timezone import now
@login_required
def cambiar_estado_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        nuevo_estado = request.POST.get('nuevo_estado')
        inmueble_id = request.POST.get('inmueble_id')
        usuario = request.user

        if nuevo_estado == 'aceptada' and reserva.estado == 'pendiente':
            # ✅ Validar si hay otra en pendiente_pago que se superponga
            bloqueo = Reserva.objects.filter(
                inmueble=reserva.inmueble,
                estado='pendiente_pago',
                fecha_inicio__lt=reserva.fecha_fin,
                fecha_fin__gt=reserva.fecha_inicio
            ).exclude(pk=reserva.pk).first()

            if bloqueo:
                tiempo_restante = bloqueo.fecha_pendiente_pago + timedelta(minutes=3) - now()
                minutos = int(tiempo_restante.total_seconds() // 60)
                segundos = int(tiempo_restante.total_seconds() % 60)
                messages.error(request, f"Ya hay una reserva pendiente de pago que bloquea estas fechas. Esperá {minutos}m {segundos}s.")
                return redirect('inmueble_detalle', pk=inmueble_id)

            # ✅ Si no hay conflicto, aceptar como pendiente de pago
            reserva.estado = 'pendiente_pago'
            reserva.fecha_pendiente_pago = now()
            reserva.save()
            send_mail(
                'Estado de Reserva:',
                'Su solicitud de reserva queda pendiente de pago.',
                'no-reply@tuapp.com',
                [usuario.email],
                fail_silently=False,
            )

        elif nuevo_estado == 'rechazada' and reserva.estado == 'pendiente':
            reserva.estado = 'rechazada'
            reserva.save()
            send_mail(
                'Estado de Reserva:',
                'Su solicitud de reserva ha sido rechazada.',
                'no-reply@tuapp.com',
                [usuario.email],
                fail_silently=False,
            )

        return redirect('inmueble_detalle', pk=inmueble_id)


def inmueble_detalle(request, pk):
    inmueble_base = get_object_or_404(Inmueble, pk=pk)
    inmueble = get_object_or_404(Inmueble, pk=pk)
    puede_cambiar_estado = False  # valor por defecto

    # Determinar tipo específico del inmueble
    try:
        tipo_obj = Departamento.objects.get(pk=pk)
        tipo = "Departamento"
    except Departamento.DoesNotExist:
        try:
            tipo_obj = Casa.objects.get(pk=pk)
            tipo = "Casa"
        except Casa.DoesNotExist:
            try:
                tipo_obj = Local.objects.get(pk=pk)
                tipo = "Local"
            except Local.DoesNotExist:
                try:
                    tipo_obj = Cochera.objects.get(pk=pk)
                    tipo = "Cochera"
                except Cochera.DoesNotExist:
                    tipo_obj = inmueble_base
                    tipo = "Desconocido"

    # Cargar reservas
    reservas = Reserva.objects.none()  # Default para no autenticados

    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            reservas = Reserva.objects.filter(inmueble=inmueble)
            puede_cambiar_estado = True
        else:
            reservas = Reserva.objects.filter(
                inmueble=inmueble,
                usuario=request.user,
                estado__in=['pendiente_pago', 'aceptada', 'pendiente']
            )
    
    reservas_aceptadas = reservas.filter(estado='aceptada')
    reservas_pendientes = reservas.filter(estado__in=['pendiente_pago', 'pendiente'])

    context = {
        'inmueble': tipo_obj,
        'reservas_aceptadas': reservas_aceptadas,
        'reservas_pendientes': reservas_pendientes,
        'puede_cambiar_estado': puede_cambiar_estado,
        'user': request.user,
        'estados_cancelables': ['pendiente', 'pendiente_pago', 'aceptada'],
    }
    return render(request, 'gestion_inmuebles/detalle_inmueble.html', context)
from datetime import timedelta

@login_required
def pagar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    reserva.estado = "aceptada"
    reserva.save()
    if reserva.estado != 'pendiente_pago':
        return HttpResponseForbidden("Esta reserva no se puede pagar.")

    total_a_pagar = calcular_total_reserva(reserva)

    if request.method == "POST":
        form = PagoForm(request.POST)
        usuario = request.user
        if form.is_valid():
            numero = form.cleaned_data["numero"]
            titular = form.cleaned_data["titular"]
            codigo = form.cleaned_data["codigo"]

            try:
                tarjeta = Tarjeta.objects.get(numero=numero, titular=titular, codigo=codigo)
            except Tarjeta.DoesNotExist:
                form.add_error(None, "Los datos de la tarjeta son incorrectos.")
                return render(request, "gestion_reserva/pagar_reserva.html", {
                    "form": form, "reserva": reserva, "total": total_a_pagar
                })
            
            if tarjeta.monto_disponible < total_a_pagar:
                form.add_error(None, "Saldo insuficiente en la tarjeta.")
                return render(request, "gestion_reserva/pagar_reserva.html", {
                    "form": form, "reserva": reserva, "total": total_a_pagar
                })

            tarjeta.monto_disponible -= total_a_pagar
            tarjeta.save()

            reserva.estado = "aceptada"
            reserva.save()

            send_mail(
                'Estado de Pago:',
                'Se ha acreditado el pago de la reserva correctamente',
                'no-reply@tuapp.com',
                [usuario.email],
                fail_silently=False,
            )

            if reserva.inmueble.tipo != "Cochera":
                conflictos = Reserva.objects.filter(
                    inmueble=reserva.inmueble,
                    estado__in=['pendiente', 'pendiente_pago'],
                    fecha_inicio__lt=reserva.fecha_fin,
                    fecha_fin__gt=reserva.fecha_inicio
                ).exclude(pk=reserva.pk)

                for r in conflictos:
                    r.estado = 'rechazada'
                    r.save()
            else:
                cochera = Cochera.objects.get(pk=reserva.inmueble.pk)
                conflictos = Reserva.objects.filter(
                    inmueble=reserva.inmueble,
                    estado__in=['pendiente', 'pendiente_pago'],
                    fecha_inicio__lt=reserva.fecha_fin,
                    fecha_fin__gt=reserva.fecha_inicio).exclude(pk=reserva.pk)
                aceptadas = Reserva.objects.filter(
                    inmueble=reserva.inmueble,
                    estado='aceptada',
                    fecha_inicio__lt=reserva.fecha_fin,
                    fecha_fin__gt=reserva.fecha_inicio)
                if aceptadas.count() == cochera.plazas:
                    for r in conflictos:
                        r.estado = 'rechazada'
                        r.save()

            return redirect("inmueble_detalle", pk=reserva.inmueble.id)
    else:
        form = PagoForm()

    return render(request, "gestion_reserva/pagar_reserva.html", {
        "form": form,
        "reserva": reserva,
        "total": total_a_pagar
    })

@login_required
def cancelar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)

    
    usuario = request.user
    if reserva.estado in ['pendiente', 'pendiente_pago','aceptada']:
        
        messages.success(request, "Reserva cancelada correctamente.")
        if (reserva.estado == 'aceptada'):
             send_mail(
             'Estado de Reserva:',
             'Su reserva ha sido cancelada. Poltica de Cancelacion: ' + reserva.inmueble.politica_cancelacion,
             'no-reply@tuapp.com',
             [usuario.email],
             fail_silently=False,
    )        
        else:
             send_mail(
             'Estado de Reserva:',
             'Su reserva ha sido cancelada.',
             'no-reply@tuapp.com',
             [usuario.email],
             fail_silently=False,
    )          
        reserva.estado = 'cancelada'
        reserva.save()     
    else:
        messages.error(request, "No se puede cancelar esta reserva.")
    if(usuario.is_staff or usuario.is_superuser):
        return redirect('inmueble_detalle', pk=reserva.inmueble.id)
    else:
        return redirect('listar_reservas')

from datetime import timedelta

def calcular_total_reserva(reserva):
    duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
    duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
    if duracion_dias == 0:
        duracion_dias = 1

    precio = float(reserva.inmueble.precio)
    tiempo = reserva.inmueble.tiempo

    if tiempo == 'Por_hora':
        return round(precio * duracion_horas, 2)
    elif tiempo == 'Por_noche':
        return round(precio * duracion_dias, 2)
    elif tiempo == 'Por_semana':
        return round(precio * (duracion_dias / 7), 2)
    elif tiempo == 'Por_mes':
        return round(precio * (duracion_dias / 30), 2)
    else:
        return round(precio * duracion_dias, 2)


from datetime import timedelta

def calcular_total_reserva(reserva):
    duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
    duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
    if duracion_dias == 0:
        duracion_dias = 1

    precio = float(reserva.inmueble.precio)
    tiempo = reserva.inmueble.tiempo

    if tiempo == 'Por_hora':
        return round(precio * duracion_horas, 2)
    elif tiempo == 'Por_noche':
        return round(precio * duracion_dias, 2)
    elif tiempo == 'Por_semana':
        return round(precio * (duracion_dias / 7), 2)
    elif tiempo == 'Por_mes':
        return round(precio * (duracion_dias / 30), 2)
    else:
        return round(precio * duracion_dias, 2)
