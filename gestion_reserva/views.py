from django.shortcuts import render, redirect
from .forms import CampoReservaNormal, CampoReservaCochera, CampoReservaPago
# Create your views here.
def pagina_prueba(request):
    return render(request, 'gestion_reserva/prueba_reserva.html')

def campo_reserva_normal(request):
    form = CampoReservaNormal(request.POST or None, request.FILES or None)

    context = {
        'form': form
    }

    return render(request, 'gestion_reservas/campo_generico_reserva.html', context)

def campo_reserva_cochera(request):
    form = CampoReservaCochera(request.POST or None, request.FILES or None)

    context = {
        'form': form
    }

    return render(request, 'gestion_reservas/campo_generico_reserva.html', context)