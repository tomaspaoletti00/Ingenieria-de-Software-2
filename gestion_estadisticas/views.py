from django.shortcuts import render
from django.db import models
from gestion_reserva.models import Reserva
from django.db.models import Sum, Q
from django.db.models.functions import TruncYear, TruncMonth, TruncDay
from gestion_usuarios.models import Usuario
from django.db.models import F, ExpressionWrapper, FloatField, DurationField
import math
from datetime import datetime
from gestion_inmuebles.models import Inmueble
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Cast
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, DurationField, FloatField, DecimalField, Sum, Q, Value
from datetime import datetime
from decimal import Decimal
from gestion_reserva.views import calcular_total_reserva

def menu_estadisticas(request):
    return render(request, 'gestion_estadisticas/menu-estadisticas.html')





def ingresos_mensuales(request):
    reservas = Reserva.objects.filter(estado="aceptada").select_related('inmueble')

    ingresos_por_mes = {}

    for reserva in reservas:
        inmueble_base = reserva.inmueble
        inmueble = inmueble_base.get_subclass()

        duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
        duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
        if duracion_dias == 0:
            duracion_dias = 1

        precio = float(inmueble.precio)

        # Asignamos 'tiempo' según el tipo de inmueble
        tipo = inmueble.tipo
        if tipo == 'Cochera':
            tiempo = 'Por_hora'
        elif tipo == 'Departamento':
            tiempo = 'Por_dia'
        elif tipo == 'Casa':
            tiempo = 'Por_dia'
        elif tipo == 'Local':
            tiempo = 'Por_mes'
        else:
            tiempo = 'Por_dia'  # fallback

        if tiempo == 'Por_hora':
            total = precio * duracion_horas
        elif tiempo == 'Por_noche':
            total = precio * duracion_dias
        elif tiempo == 'Por_semana':
            total = precio * (duracion_dias / 7)
        elif tiempo == 'Por_mes':
            total = precio * (duracion_dias / 30)
        else:
            total = precio * duracion_dias

        mes = reserva.fecha_inicio.strftime("%B %Y")
        ingresos_por_mes[mes] = ingresos_por_mes.get(mes, 0) + total

    def parse_mes(mes_str):
        return datetime.strptime(mes_str, "%B %Y")

    labels = sorted(ingresos_por_mes.keys(), key=parse_mes)
    valores = [round(ingresos_por_mes[mes], 2) for mes in labels]
    total_ingresos = sum(valores)

    return render(request, "gestion_estadisticas/ingresos.html", {
        "labels": labels,
        "valores": valores,
        "total_ingresos": total_ingresos,
    })




def ingresos_por_inmueble(request):
    query = request.GET.get("q", "")
    reservas = Reserva.objects.filter(estado="aceptada").select_related("inmueble")

    ingresos_dict = {}

    for reserva in reservas:
        inmueble = reserva.inmueble

        duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
        duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
        if duracion_dias == 0:
            duracion_dias = 1

        try:
            tiempo = inmueble.tiempo
        except AttributeError:
            tiempo = None

        precio = float(inmueble.precio)

        if tiempo == "Por_hora":
            total = precio * duracion_horas
        elif tiempo == "Por_noche":
            total = precio * duracion_dias
        elif tiempo == "Por_semana":
            total = precio * (duracion_dias / 7)
        elif tiempo == "Por_mes":
            total = precio * (duracion_dias / 30)
        else:
            total = precio * duracion_dias

        if inmueble.nombre in ingresos_dict:
            ingresos_dict[inmueble.nombre]["total"] += total
        else:
            ingresos_dict[inmueble.nombre] = {
                "inmueble": inmueble,
                "total": total
            }

    # Filtrar por nombre si hay query
    if query:
        ingresos_dict = {
            nombre: data
            for nombre, data in ingresos_dict.items()
            if query.lower() in nombre.lower()
        }

    ingresos = sorted(
        ingresos_dict.values(),
        key=lambda x: x["total"],
        reverse=True
    )

    return render(request, "gestion_estadisticas/ingresos-inmueble.html", {
        "ingresos": ingresos,
        "query": query,
    })


def ingresos_por_tipo(request):
    # Traemos reservas aceptadas con inmueble para evitar consultas extras
    reservas = Reserva.objects.filter(estado="aceptada").select_related('inmueble')

    # Calculamos el monto de cada reserva según duración y precio
    ingresos_por_tipo = {}

    for reserva in reservas:
        inmueble = reserva.inmueble
        tipo = inmueble.tipo

        duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
        if duracion_dias == 0:
            duracion_dias = 1  # mínimo 1 día para no dar cero

        precio = float(inmueble.precio)
        tiempo = getattr(inmueble, 'tiempo', 'Por_dia')  # fallback a día si no existe tiempo

        if tiempo == 'Por_hora':
            duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
            total = precio * duracion_horas
        elif tiempo == 'Por_noche':
            total = precio * duracion_dias
        elif tiempo == 'Por_semana':
            total = precio * (duracion_dias / 7)
        elif tiempo == 'Por_mes':
            total = precio * (duracion_dias / 30)
        else:
            total = precio * duracion_dias

        ingresos_por_tipo[tipo] = ingresos_por_tipo.get(tipo, 0) + total

    # Preparamos datos para el gráfico
    labels = list(ingresos_por_tipo.keys())
    valores = [round(ingresos_por_tipo[t], 2) for t in labels]

    return render(request, 'gestion_estadisticas/ingresos-tipo.html', {
        'labels': labels,
        'valores': valores,
    })

def porcentaje_reservas_por_tipo(request):
    # Filtrar solo reservas aceptadas
    reservas = Reserva.objects.filter(estado="aceptada").select_related("inmueble")

    # Contador por tipo
    conteo_por_tipo = {}
    total_reservas = 0

    for reserva in reservas:
        tipo = getattr(reserva.inmueble, "tipo", "Otro")
        conteo_por_tipo[tipo] = conteo_por_tipo.get(tipo, 0) + 1
        total_reservas += 1

    # Calcular porcentaje por tipo
    porcentajes = {}
    for tipo, cantidad in conteo_por_tipo.items():
        porcentaje = (cantidad / total_reservas) * 100 if total_reservas > 0 else 0
        porcentajes[tipo] = round(porcentaje, 2)

    # Preparar datos para el gráfico o tabla
    labels = list(porcentajes.keys())
    valores = list(porcentajes.values())

    return render(request, 'gestion_estadisticas/porcentaje-tipo.html', {
        "labels": labels,
        "valores": valores,
        "total_reservas": total_reservas
    })

def total_ingresos(request):
    reservas = Reserva.objects.filter(estado="aceptada").select_related("inmueble")
    total_general = 0

    for reserva in reservas:
        inmueble = reserva.inmueble
        precio = float(inmueble.precio)

        if inmueble.tipo == "Cochera":
            # Total por horas
            duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
            total = precio * duracion_horas
        else:
            # Total por noches (mínimo 1 noche)
            duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
            if duracion_dias == 0:
                duracion_dias = 1
            total = precio * duracion_dias

        total_general += total

    total_general = round(total_general, 2)

    return render(request, "gestion_estadisticas/ingresos-total.html", {
        "total_general": total_general
    })

def estadistica_ingresos_diario(request):
    reservas_aceptadas = Reserva.objects.filter(estado="aceptada").select_related("inmueble")

    # Obtener días únicos con reservas aceptadas
    dias_con_ingresos = reservas_aceptadas.annotate(dia=TruncDay('fecha_inicio')) \
                                          .values_list('dia', flat=True).distinct().order_by('dia')

    dias_str = [d.strftime('%Y-%m-%d') for d in dias_con_ingresos]

    fecha_str = request.GET.get('fecha')
    total_ingresos = 0
    fecha_mostrada = None
    reservas_del_dia = []

    if fecha_str:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            reservas_filtradas = reservas_aceptadas.filter(fecha_inicio__date=fecha)
            total_ingresos = sum(calcular_total_reserva(r) for r in reservas_filtradas)
            fecha_mostrada = fecha
            reservas_del_dia = reservas_filtradas
        except ValueError:
            pass  # Fecha inválida ignorada

    return render(request, 'gestion_estadisticas/estadistica_ingresos_diario.html', {
        'dias_habilitados': dias_str,
        'total_ingresos': round(total_ingresos, 2),
        'fecha_mostrada': fecha_mostrada,
        'reservas': reservas_del_dia,
    })