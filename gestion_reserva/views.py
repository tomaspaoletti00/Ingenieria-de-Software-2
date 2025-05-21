import json

from django.shortcuts import render, redirect
from .forms import ReservaNormalForm, ReservaCocheraForm
from gestion_inmuebles.models import Inmueble
from .models import Reserva
from django.http import JsonResponse

# Create your views here.
def pagina_prueba(request):
    return render(request, 'gestion_reserva/prueba_reserva.html')

def campo_reserva_normal(request):
    form = ReservaNormalForm(request.POST or None, request.FILES or None)

    context = {
        'form': form
    }

    return render(request, 'gestion_reserva/campo_generico_reserva.html', context)

def campo_reserva_cochera(request):
    form = ReservaCocheraForm(request.POST or None, request.FILES or None)

    context = {
        'form': form
    }

    return render(request, 'gestion_reserva/campo_generico_reserva.html', context)


def realizar_reserva(request):
    if request.method == "POST":
        data = json.loads(request.body)

        inmueble_id = request.GET.get("inmueble_id")  # o como lo manejes
        inmueble = Inmueble.objects.get(id=inmueble_id)

        reserva = Reserva.objects.create(
            usuario=request.user,
            inmueble=inmueble,
            fecha_inicio=data['fecha_inicio'],
            fecha_fin=data['fecha_fin'],
            tipo='normal',
            metodo_pago=data['metodo_pago'],
            datos_inquilinos=data['personas'],
            estado='pendiente'
        )
        return JsonResponse({"mensaje": "Reserva creada"})