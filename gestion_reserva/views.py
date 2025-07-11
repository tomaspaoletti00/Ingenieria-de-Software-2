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
    if not dia_str:
        return JsonResponse({"horas_ocupadas": []})
    try:
        dia = datetime.strptime(dia_str, "%Y-%m-%d").date()
        cochera = Cochera.objects.get(pk=inmueble_id)
    except (ValueError, Cochera.DoesNotExist):
        return JsonResponse({"horas_ocupadas": []})

    reservas = Reserva.objects.filter(
        inmueble=cochera,
        fecha_inicio__date=dia,
        estado__in=["aceptada", "pendiente_pago"],
        
    )

    horas = defaultdict(int)
    for r in reservas:
        for h in range(r.fecha_inicio.hour, r.fecha_fin.hour):
            horas[h] += 1

    horas_ocupadas = [h for h, count in horas.items() if count >= cochera.plazas]
    return JsonResponse({"horas_ocupadas": horas_ocupadas})

def obtener_cant_inquilino(tipo_inmueble, id_inmueble):
    if tipo_inmueble == "Casa":
        return Casa.objects.get(pk=id_inmueble).cantidad_inquilinos
    elif tipo_inmueble == "Departamento":
        return Departamento.objects.get(pk=id_inmueble).cantidad_inquilinos
    return 1

from django.shortcuts import redirect

@login_required
def agregarInquilinos(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id, usuario=request.user)
    inmueble = reserva.inmueble
    tipo_inmueble = inmueble.tipo
    cant_inquilino = obtener_cant_inquilino(tipo_inmueble, inmueble)

    if request.method == "POST":
        datos_inquilinos = json.loads(request.POST.get("datos_inquilinos", "[]"))
        print("datos_inquilinos recibido:", datos_inquilinos)
        reserva.datos_inquilinos = datos_inquilinos
        reserva.save()
        return redirect("pagar_reserva", reserva_id=reserva.id)  # 🔁 REDIRECCIÓN
            
    

    return render(request, "gestion_reserva/insertar_inquilino.html", {
        "usuario": request.user,
        "cant_inquilino": cant_inquilino,
        "tipo_inmueble": tipo_inmueble,
        "inmueble": inmueble,
        "reserva": reserva,
    })

                   

@login_required
def hacer_reserva(request, id_inmueble):
    inmueble = get_object_or_404(Inmueble, pk=id_inmueble)
    tipo_inmueble = inmueble.tipo

    FormClase = ReservaCocheraForm if tipo_inmueble == "Cochera" else ReservaNormalForm
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
        Q(estado='aceptada') | Q(estado='', fecha_pendiente_pago__gte=tiempo_limite_pago)
    ).values_list('fecha_inicio', 'fecha_fin')
    
    if request.method == "POST":
        form = FormClase(request.POST, inmueble=inmueble)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.inmueble = inmueble
            reserva.datos_inquilinos=[]
            reserva.save()
            messages.success(request, 'Reserva exitosa.')
            return redirect("inmueble_detalle", pk=inmueble.id)
    else:
        form = FormClase(inmueble=inmueble)

    # Obtener días bloqueados para cochera
    dias_bloqueados = getattr(form, "dias_bloqueados", [])

    # Obtener fechas ocupadas para reservas normales
    fechas_ocupadas = []
    if tipo_inmueble != "Cochera":
        for inicio, fin in conflictos:
            actual = inicio.date()
            while actual <= fin.date():
                fechas_ocupadas.append(actual.isoformat())
                actual += timedelta(days=1)

    return render(request, "gestion_reserva/hacer_reserva.html", {
        "form": form,
        "tipo_inmueble": tipo_inmueble,
        "inmueble": inmueble,
        "usuario": request.user,
        "fechas_ocupadas": fechas_ocupadas,
        "dias_bloqueados": dias_bloqueados,
    })
@login_required
def listar_reservas(request):
    reservas_aceptadas = Reserva.objects.filter(usuario=request.user, estado__in=['aceptada', 'en_curso'])
    reservas_pendientes = Reserva.objects.filter(usuario=request.user,estado__in=['pendiente_pago', 'pendiente'])
    reservas_canceladas = Reserva.objects.filter(usuario=request.user, estado='cancelada')
    reservas_finalizadas = Reserva.objects.filter(usuario=request.user, estado='finalizada')
    puede_cambiar_estado = False  # Solo para admins o empleados, si querés podés condicionar

    return render(request, 'gestion_reserva/listar_reservas.html', {
        'reservas_aceptadas': reservas_aceptadas,
        'reservas_pendientes': reservas_pendientes,
        'reservas_canceladas': reservas_canceladas,
        'reservas_finalizadas': reservas_finalizadas,
        'puede_cambiar_estado': puede_cambiar_estado,
        'user': request.user,  # Por si lo necesitás en la tabla
        'estados_cancelables': ['pendiente', 'pendiente_pago', 'aceptada'],
    })

from django.utils.timezone import now
@login_required

def cambiar_estado_reserva(request, reserva_id):
    limite_minutos = 3
    tiempo_limite_pago = timezone.now() - timedelta(minutes=limite_minutos)

    expiradas = Reserva.objects.filter(
        estado='pendiente_pago',
        fecha_pendiente_pago__lt=tiempo_limite_pago
    )
    for res in expiradas:
        res.estado = 'cancelada'
        res.save()

    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        nuevo_estado = request.POST.get('nuevo_estado')
        inmueble_id = request.POST.get('inmueble_id')
        usuario = request.user

        if nuevo_estado == 'aceptada' and reserva.estado == 'pendiente':
            # --- LÓGICA ESPECIAL PARA COCHERA ---
            
            if reserva.inmueble.tipo == "Cochera":
                try:
                    cochera = Cochera.objects.get(pk=reserva.inmueble.pk)
                except Cochera.DoesNotExist:
                    messages.error(request, "Cochera no encontrada.")
                    return redirect('inmueble_detalle', pk=inmueble_id)

                # Reservas aceptadas o pendiente_pago, excepto la actual
                reservas = Reserva.objects.filter(
                    inmueble=reserva.inmueble,
                    estado__in=["aceptada", "pendiente_pago"],
                    fecha_inicio__lt=reserva.fecha_fin,
                    fecha_fin__gt=reserva.fecha_inicio
                ).exclude(pk=reserva.pk)

                horas_ocupadas = defaultdict(int)
                for r in reservas:
                    h_ini = r.fecha_inicio.hour
                    h_fin = r.fecha_fin.hour
                    for h in range(h_ini, h_fin):
                        horas_ocupadas[h] += 1

                h_reserva_ini = reserva.fecha_inicio.hour
                h_reserva_fin = reserva.fecha_fin.hour
                for h in range(h_reserva_ini, h_reserva_fin):
                    if horas_ocupadas[h] >= cochera.plazas:
                        messages.error(request, f"Ya hay reservas pendientes o aceptadas que completan las plazas en la franja {h:02}:00.")
                        return redirect('inmueble_detalle', pk=inmueble_id)

            else:
                # --- LÓGICA GENERAL PARA NO COCHERAS ---
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
            messages.success(request, 'Reserva aceptada.')

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
            messages.success(request, 'Reserva rechazada.')

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
    
    reservas_aceptadas = reservas.filter(estado__in=['aceptada', 'en_curso'])
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

            messages.success(request, 'Reserva pagada.')
            return redirect('listar_reservas')
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
        messages.success(request, 'Reserva cancelada')     
    else:
        messages.error(request, "No se puede cancelar esta reserva.")
    if(usuario.is_staff or usuario.is_superuser):
        return redirect('inmueble_detalle', pk=reserva.inmueble.id)
    else:
        return redirect('listar_reservas')

from datetime import timedelta

def calcular_total_reserva(reserva):
    tipo = reserva.inmueble.tipo.lower()  # Por si viene con mayúsculas
    duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
    duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
    if duracion_dias == 0:
        duracion_dias = 1

    if tipo == "cochera":
        precio = float(reserva.inmueble.precio) * duracion_horas
    else:
        precio = float(reserva.inmueble.precio) * duracion_dias

    return precio

@login_required
def cancelar_reserva_admin(request, reserva_id):
    if not (request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("No tenés permisos para acceder a esta acción.")

    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == "POST":
        motivo = request.POST.get("motivo", "").strip()

        if reserva.estado in ['pendiente', 'pendiente_pago', 'aceptada']:
            reserva.estado = 'cancelada'
            reserva.save()

            mensaje = f"Su reserva fue cancelada por un administrador.\nMotivo: {motivo}" if motivo else "Su reserva fue cancelada por un administrador."
            send_mail(
                'Reserva cancelada por administrador',
                mensaje,
                'no-reply@tuapp.com',
                [reserva.usuario.email],
                fail_silently=False,
            )
            messages.success(request, "Reserva cancelada y mail enviado.")
        else:
            messages.error(request, "No se puede cancelar esta reserva.")
        return redirect('inmueble_detalle', pk=reserva.inmueble.id)

    return render(request, "gestion_reserva/cancelar_reserva_admin.html", {
        "reserva": reserva
    })

@login_required
def actualizar_estado_dinamico(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if reserva.usuario != request.user and not request.user.is_staff and not request.user.is_superuser:
        return HttpResponseForbidden("No tenés permiso.")

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'iniciar' and reserva.estado == 'aceptada':
            reserva.estado = 'en_curso'
            reserva.save()
            messages.success(request, "La reserva se ha iniciado.")
        elif accion == 'finalizar' and reserva.estado == 'en_curso':
            reserva.estado = 'finalizada'
            reserva.save()
            messages.success(request, "La reserva se ha finalizado.")
        else:
            messages.error(request, "Acción no permitida.")

    return redirect('inmueble_detalle', pk=reserva.inmueble.id)



