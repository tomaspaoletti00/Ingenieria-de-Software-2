from django.shortcuts import render

from django.shortcuts import render, redirect
from .forms import InmuebleForm

def crear_inmueble(request):
    if request.method == 'POST':
        form = InmuebleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_inmuebles')  # o donde quieras redirigir
    else:
        form = InmuebleForm()
    return render(request, 'gestion_inmuebles/crear_inmueble.html', {'form': form})
