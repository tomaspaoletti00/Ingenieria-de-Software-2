import json
from django.shortcuts import render, redirect
from .forms import ReservaNormalForm, ReservaCocheraForm
from gestion_inmuebles.models import Inmueble, Casa, Departamento
from django.http import JsonResponse
from .models import Reserva

# Create your views here.

def obtener_cant_inquilino(tipo_inmueble, id_inmueble):
    cant_default = 1
    if (tipo_inmueble == "Casa"):
        casa_aux = Casa.objects.get(pk=id_inmueble)
        cant_default = casa_aux.cantidad_inquilinos
    elif (tipo_inmueble == "Departamento"):
        depto_aux = Departamento.objects.get(pk=id_inmueble)
        cant_default = depto_aux.cantidad_inquilinos
    return cant_default

def hacer_reserva(request, id_inmueble):
    inmueble = Inmueble.objects.get(id=id_inmueble)
    tipo_inmueble = inmueble.tipo
    cant_inquilino = obtener_cant_inquilino(tipo_inmueble, id_inmueble)

    if request.method == "POST":
        form = ReservaCocheraForm(request.POST) if tipo_inmueble == "Cochera" else ReservaNormalForm(request.POST)

        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.usuario = request.user
            reserva.inmueble = inmueble  # 👈 ACÁ ESTÁ EL PUNTO CLAVE
            reserva.datos_inquilinos = json.loads(request.POST.get("datos_inquilinos", "[]"))
            reserva.save()
            return redirect("inmueble_detalle", pk=inmueble.id)
        else:
            return JsonResponse({"error": form.errors.as_json()}, status=400)
    else:
        form = ReservaCocheraForm(initial={"inmueble": inmueble}) if tipo_inmueble == "Cochera" else ReservaNormalForm(initial={"inmueble": inmueble})


    context = {
        "form": form,
        "cant_inquilino": cant_inquilino
    }

    return render(request, 'gestion_reserva/hacer_reserva.html', context)