from django.shortcuts import render
from django.db import models
from gestion_reserva.models import Reserva
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from gestion_usuarios.models import Usuario
from django.db.models import F, ExpressionWrapper, FloatField, DurationField
import math
from datetime import datetime
from gestion_inmuebles.models import Inmueble
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Cast
from datetime import timedelta
from django.db.models import F, ExpressionWrapper, DurationField, FloatField, DecimalField, Sum, Q, Value


def menu_estadisticas(request):
    return render(request, 'gestion_estadisticas/menu-estadisticas.html')


def ingresos_mensuales(request):
    # Traemos reservas aceptadas con inmueble para no hacer consultas extra
    reservas = Reserva.objects.filter(estado="aceptada").select_related('inmueble')

    ingresos_por_mes = {}

    for reserva in reservas:
        inmueble = reserva.inmueble

        duracion_horas = (reserva.fecha_fin - reserva.fecha_inicio).total_seconds() / 3600
        duracion_dias = (reserva.fecha_fin.date() - reserva.fecha_inicio.date()).days
        if duracion_dias == 0:
            duracion_dias = 1  # mínimo 1 día para no calcular cero

        precio = float(inmueble.precio)
        tiempo = inmueble.tiempo

        if tiempo == 'Por_hora':
            total = precio * duracion_horas
        elif tiempo == 'Por_noche':
            total = precio * duracion_dias
        elif tiempo == 'Por_semana':
            total = precio * (duracion_dias / 7)
        elif tiempo == 'Por_mes':
            total = precio * (duracion_dias / 30)
        else:
            total = precio * duracion_dias  # fallback simple

        mes = reserva.fecha_inicio.strftime("%B %Y")
        ingresos_por_mes[mes] = ingresos_por_mes.get(mes, 0) + total

    # Ordenamos cronológicamente
    def parse_mes(mes_str):
        return datetime.strptime(mes_str, "%B %Y")

    labels = sorted(ingresos_por_mes.keys(), key=parse_mes)
    valores = [round(ingresos_por_mes[mes], 2) for mes in labels]

    print(f"Debug:")
    print(f"Reservas aceptadas: {reservas.count()}")
    for mes, total in ingresos_por_mes.items():
        print(f"Mes: {mes} - Total ingresos: {total}")

    total_ingresos = sum(ingresos_por_mes.values())
    return render(request, "gestion_estadisticas/ingresos.html", {
        "labels": labels,
        "valores": valores,
        "total_ingresos": total_ingresos,
    })





def ingresos_por_inmueble(request):
    query = request.GET.get('q', '')

    reservas = Reserva.objects.filter(
        inmueble__nombre__icontains=query
    )

    reservas = reservas.annotate(
        dias=ExpressionWrapper(
            F('fecha_fin') - F('fecha_inicio'),
            output_field=DurationField()
        )
    )

    reservas = reservas.annotate(
        dias_float=Cast(F('dias'), output_field=FloatField()) / (24 * 3600)
    )

    reservas = reservas.annotate(
        monto_estimado=ExpressionWrapper(
            F('inmueble__precio') * F('dias_float'),
            output_field=DecimalField(max_digits=12, decimal_places=2)
        )
    )

    ingresos = (
        reservas.values('inmueble__id', 'inmueble__nombre')
        .annotate(monto_total=Sum('monto_estimado'))
        .order_by('-monto_total')
    )

    return render(request, 'gestion_estadisticas/ingresos-inmueble.html', {
        'ingresos': ingresos,
        'query': query,
    })
