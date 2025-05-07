from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import InmuebleForm
from .models import Inmueble

def adminInmuebles(request):
    return render(request, 'gestion_inmuebles/adminInmuebles.html')

def crear_inmueble(request):
    if request.method == 'POST':
        form = InmuebleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('homeInmuebles')  # o donde quieras redirigir
    else:
        form = InmuebleForm()
    return render(request, 'gestion_inmuebles/crear_inmueble.html', {'form': form})

def listarInmuebles(request):
    inmuebles = Inmueble.objects.all()  # Esto sería el equivalente a SELECT * FROM inmueble
    return render(request, 'gestion_inmuebles/listaInmuebles.html', {'inmuebles': inmuebles})