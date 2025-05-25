from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from gestion_inmuebles.models import Departamento, Casa, Local, Cochera
from .forms import InmuebleForm, FormularioDepartamento, FormularioCasa, FormularioLocal, FormularioCochera
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

def listar_Inmuebles(request):
    tipo_filtro = request.GET.get('tipo')
    orden_superficie = request.GET.get("superficie")
    orden_precio = request.GET.get("orden_precio")
    

    inmuebles_base = Inmueble.objects.filter(estado="Disponible", activo="True")

    if orden_superficie == "asc":
        inmuebles_base = inmuebles_base.order_by("superficie")
    elif orden_precio == "desc":
        inmuebles_base = inmuebles_base.order_by("-superficie")
    

    if orden_precio == "asc":
        inmuebles_base = inmuebles_base.order_by("precio")
    elif orden_precio == "desc":
        inmuebles_base = inmuebles_base.order_by("-precio")

    if tipo_filtro:
        inmuebles_base = inmuebles_base.filter(tipo=tipo_filtro)
    if orden_superficie:
        inmuebles_base = inmuebles_base.filter(superficie_iexact=orden_superficie)

    inmuebles = []

    for inmueble in inmuebles_base:
        try:
            tipo_obj = Departamento.objects.get(pk=inmueble.pk)
            tipo = "Departamento"
        except Departamento.DoesNotExist:
            try:
                tipo_obj = Casa.objects.get(pk=inmueble.pk)
                tipo = "Casa"
            except Casa.DoesNotExist:
                try:
                    tipo_obj = Local.objects.get(pk=inmueble.pk)
                    tipo = "Local"
                except Local.DoesNotExist:
                    try:
                        tipo_obj = Cochera.objects.get(pk=inmueble.pk)
                        tipo = "Cochera"
                    except Cochera.DoesNotExist:
                        continue

        if not tipo_filtro or tipo.lower() == tipo_filtro.lower():
            inmuebles.append({'tipo': tipo, 'objeto': tipo_obj})

    return render(request, 'gestion_inmuebles/listaInmuebles.html', {
        'inmuebles': inmuebles,
        'tipo': tipo_filtro,
    })

# Esto es todo lo de la parte para agregar inmuebles de los cuatro tipos
# Hay varios def con codigo muy parecido, si fuera oo2 seria como un homicidio triple
# Despues le hago refactoring lo importante es que anda y se guarda en la base de datos

def formulario_inmueble(request):
    return render(request, 'gestion_inmuebles/formulario_inmueble.html')



def crear_formulario(request):
    formulario_tipo = {
        'departamento': crear_departamento,
        'casa': crear_casa,
        'local': crear_local,
        'cochera': crear_cochera
    }

    tipo = request.GET.get('tipo')

    if tipo not in formulario_tipo.keys():
        return redirect('gestion_inmuebles/formulario_inmueble.html')

    return formulario_tipo[tipo](request)

def crear_departamento(request):
    form = FormularioDepartamento(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'tipo': 'departamento'
    }

    if form.is_valid():
        form.save()
        redirect('gestion_inmuebles/formulario_inmueble.html')

    return render(request, 'gestion_inmuebles/formulario_generico.html', context)


def crear_casa(request):
    form = FormularioCasa(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'tipo': 'casa'
    }

    if form.is_valid():
        form.save()
        redirect('gestion_inmuebles/formulario_inmueble.html')

    return render(request, 'gestion_inmuebles/formulario_generico.html', context)

def crear_local(request):
    form = FormularioLocal(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'tipo': 'local'
    }

    if form.is_valid():
        form.save()
        redirect('gestion_inmuebles/formulario_inmueble.html')

    return render(request, 'gestion_inmuebles/formulario_generico.html', context)

def crear_cochera(request):
    form = FormularioCochera(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'tipo': 'cochera'
    }

    if form.is_valid():
        form.save()
        redirect('gestion_inmuebles/formulario_inmueble.html')

    return render(request, 'gestion_inmuebles/formulario_generico.html', context)

def inmueble_detalle(request, pk):
    inmueble = get_object_or_404(Inmueble, pk=pk)
    return render(request, 'gestion_inmuebles/detalle_inmueble.html', {'inmueble': inmueble})
def editar_inmueble(request, pk):
    inmueble = get_object_or_404(Inmueble, pk=pk)
    if request.method == 'POST':
        form = InmuebleForm(request.POST, request.FILES, instance=inmueble)
        if form.is_valid():
            form.save()
            return redirect('inmueble_detalle', pk=inmueble.pk)
    else:
        form = InmuebleForm(instance=inmueble)

    return render(request, 'gestion_inmuebles/editar_inmueble.html', {'form': form, 'inmueble': inmueble})
def get_real_instance(inmueble):
    for subclass in [Departamento, Casa, Local, Cochera]:
        try:
            return subclass.objects.get(pk=inmueble.pk)
        except subclass.DoesNotExist:
            continue
    return inmueble

def baja_inmueble(request, inmueble_id):
    inmueble = get_object_or_404(Inmueble, id=inmueble_id)

    if request.method == 'POST':
        inmueble.activo = False
        inmueble.save()
        messages.success(request, 'Inmueble dado de baja correctamente.')
        return redirect('listaInmuebles')

    return render(request, 'gestion_inmuebles/baja_inmueble.html', {'inmueble': inmueble})