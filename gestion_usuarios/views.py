from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Usuario
from django.shortcuts import get_object_or_404
from .forms import EditarPerfilForm

def home(request):
    return render(request, 'gestion_usuarios/home.html')

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # asegurate de tener la vista de login creada
    else:
        form = RegistroUsuarioForm()
    return render(request, 'gestion_usuarios/registro.html', {'form': form})

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                 return redirect('panel-admin')
            elif user.is_staff:
                 return redirect('panel-emp')
            else:
                 return redirect('listaInmuebles') # redirigí a la vista que quieras como home
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'gestion_usuarios/login.html')

@login_required
def logout_usuario(request):
    logout(request)
    return redirect('home')

def es_empleado(user):
    return user.is_authenticated and user.is_staff
def es_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(es_empleado)
@user_passes_test(es_admin)
def panelEmp(request):
    return render(request, 'gestion_usuarios/panel-emp.html')



@user_passes_test(es_admin)
def panelAdmin(request):
    return render(request, 'gestion_usuarios/panel-admin.html')

@login_required
@user_passes_test(es_empleado)
@user_passes_test(es_admin)
def detalle_cliente(request, user_id):
    cliente = get_object_or_404(Usuario, id=user_id, is_staff=False, is_superuser=False)
    return render(request, 'gestion_usuarios/detalle-cliente.html', {'cliente': cliente})

@login_required
@user_passes_test(es_empleado)
@user_passes_test(es_admin)
def listar_clientes(request):
    usuarios = Usuario.objects.filter(is_staff=False, is_superuser=False)
    return render(request, 'gestion_usuarios/lista-clientes.html', {'usuarios': usuarios})

@login_required
def ver_perfil(request):
     if request.method == 'POST' and 'eliminar_cuenta' in request.POST:
         request.user.delete()
         logout(request)
         return redirect('home')
         messages.success(request, 'Tu cuenta fue eliminada exitosamente.')
     return render(request, 'gestion_usuarios/perfil.html', {'usuario': request.user})

@login_required
def editar_perfil(request):
    usuario = request.user
    if request.method == 'POST':
        form = EditarPerfilForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('perfil_usuario')
    else:
        form = EditarPerfilForm(instance=usuario)
    return render(request, 'gestion_usuarios/editar_perfil.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def detalle_empleado(request, user_id):
    empleado = get_object_or_404(Usuario, id=user_id, is_staff=True, is_superuser=False)
    return render(request, 'gestion_usuarios/detalle-empleado.html', {'empleado': empleado})

@login_required
@user_passes_test(es_admin)
def listar_empleados(request):
    empleados = Usuario.objects.filter(is_staff=True, is_superuser=False)
    return render(request, 'gestion_usuarios/lista-empleados.html', {'empleados': empleados})
