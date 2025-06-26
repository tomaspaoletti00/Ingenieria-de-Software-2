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
            return redirect('listaInmuebles')  # o donde quieras redirigir
    else:
        form = InmuebleForm()
    return render(request, 'gestion_inmuebles/formulario_inmueble.html', {'form': form})

def listar_Inmuebles(request):
    tipo_filtro = request.GET.get('tipo')
    orden_superficie = request.GET.get("orden_superficie")
    orden_precio = request.GET.get("orden_precio")
    largo_plaza = request.GET.get("largo_plaza")
    ancho_plaza = request.GET.get("ancho_plaza")
    noches = request.GET.get("noches", "1")

    try:
        noches = int(noches)
        if noches < 1:
            noches = 1
    except ValueError:
        noches = 1

    inmuebles_base = Inmueble.objects.exclude(activo="0")

    if orden_superficie == "asc":
        inmuebles_base = inmuebles_base.order_by("superficie")
    elif orden_superficie == "desc":
        inmuebles_base = inmuebles_base.order_by("-superficie")

    if orden_precio == "asc":
        inmuebles_base = inmuebles_base.order_by("precio")
    elif orden_precio == "desc":
        inmuebles_base = inmuebles_base.order_by("-precio")

    if tipo_filtro:
        inmuebles_base = inmuebles_base.filter(tipo=tipo_filtro)

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

        if tipo.lower() == "cochera":
            if largo_plaza:
                try:
                    largo_plaza_val = float(largo_plaza)
                    if tipo_obj.largo_plaza < largo_plaza_val:
                        continue
                except ValueError:
                    pass
            if ancho_plaza:
                try:
                    ancho_plaza_val = float(ancho_plaza)
                    if tipo_obj.ancho_plaza < ancho_plaza_val:
                        continue
                except ValueError:
                    pass

        inmuebles.append({
            'tipo': tipo,
            'objeto': tipo_obj,
            'precio_total': tipo_obj.precio * noches,
        })
    
    precio_total = tipo_obj.precio * noches if tipo_obj.precio else 0

    return render(request, 'gestion_inmuebles/listaInmuebles.html', {
        'inmuebles': inmuebles,
        'tipo': tipo_filtro,
        'largo_plaza': largo_plaza,
        'ancho_plaza': ancho_plaza,
        'noches': noches,
    })



# Esto es todo lo de la parte para agregar inmuebles de los cuatro tipos
# Hay varios def con codigo muy parecido, si fuera oo2 seria como un homicidio triple
# Despues le hago refactoring lo importante es que anda y se guarda en la base de datos

def formulario_inmueble(request):
    tipo = request.GET.get("tipo") or request.POST.get("tipo")
    form = None

    if tipo == "departamento":
        form = FormularioDepartamento(request.POST or None, request.FILES or None)
    elif tipo == "casa":
        form = FormularioCasa(request.POST or None, request.FILES or None)
    elif tipo == "local":
        form = FormularioLocal(request.POST or None, request.FILES or None)
    elif tipo == "cochera":
        form = FormularioCochera(request.POST or None, request.FILES or None)

    if request.method == "POST" and form is not None:
        if form.is_valid():
            form.save()
            messages.success(request, 'Inmueble cargado correctamente.')
            return redirect("listaInmuebles")  # o como se llame tu redirect

    return render(request, "gestion_inmuebles/formulario_inmueble.html", {"form": form, "tipo": tipo})



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
        messages.success(request, 'Departamento cargado correctamente.')
        return redirect('listaInmuebles')

    return render(request, 'gestion_inmuebles/formulario_generico.html', context)


def crear_casa(request):
    form = FormularioCasa(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'tipo': 'casa'
    }

    if form.is_valid():
        form.save()
        messages.success(request, 'Casa cargada correctamente.')
        return redirect('listaInmuebles')

    return render(request, 'gestion_inmuebles/formulario_generico.html', context)

def crear_local(request):
    form = FormularioLocal(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'tipo': 'local'
    }

    if form.is_valid():
        form.save()
        messages.success(request, 'Local cargado correctamente.')
        return redirect('listaInmuebles')
    
    return render(request, 'gestion_inmuebles/formulario_generico.html', context)

def crear_cochera(request):
    form = FormularioCochera(request.POST or None, request.FILES or None)
    context = {
        'form': form,
        'tipo': 'cochera'
    }

    if form.is_valid():
        form.save()
        messages.success(request, 'Cochera cargada correctamente.')
        return redirect('listaInmuebles')

    return render(request, 'gestion_inmuebles/formulario_generico.html', context)

def inmueble_detalle(request, pk):
    inmueble_base = get_object_or_404(Inmueble, pk=pk)
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
    return render(request, 'gestion_inmuebles/detalle_inmueble.html', {
        'inmueble': tipo_obj,
        'tipo': tipo,
        'inmueble_base': inmueble_base,
    })
    
def editar_inmueble(request, pk):
    # Obtenemos el inmueble base
    inmueble_base = get_object_or_404(Inmueble, pk=pk)

    # Determinamos la subclase del inmueble
    if Departamento.objects.filter(pk=pk).exists():
        inmueble = Departamento.objects.get(pk=pk)
        form_class = FormularioDepartamento
    elif Casa.objects.filter(pk=pk).exists():
        inmueble = Casa.objects.get(pk=pk)
        form_class = FormularioCasa
    elif Local.objects.filter(pk=pk).exists():
        inmueble = Local.objects.get(pk=pk)
        form_class = FormularioLocal
    elif Cochera.objects.filter(pk=pk).exists():
        inmueble = Cochera.objects.get(pk=pk)
        form_class = FormularioCochera
    else:
        inmueble = inmueble_base
        form_class = InmuebleForm

    # Si se envió el formulario (POST)
    if request.method == 'POST':
        if not inmueble_base.activo:
            inmueble_base.activo = True
            inmueble_base.save()
            return redirect('listado_inmuebles_admin')

        form = form_class(request.POST, request.FILES, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inmueble editado exitosamente.')
            return redirect('listado_inmuebles_admin')
    else:
        form = form_class(instance=inmueble)

    return render(request, 'gestion_inmuebles/editar_inmueble.html', {
        'form': form,
        'inmueble': inmueble_base  # Para que el template pueda acceder al campo .activo y a la imagen
    })

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

def listar_inmuebles_admin(request):
    inmuebles = Inmueble.objects.all()
    return render(request, 'gestion_inmuebles/listaInmueblesAdmin.html', {'inmuebles': inmuebles})