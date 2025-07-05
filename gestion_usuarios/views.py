from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm,RegistroEmpleadoForm,EditarEmpleadoForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from .models import Usuario
from django.shortcuts import get_object_or_404
from .forms import EditarPerfilForm
import random
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from .models import TokenVerificacion
from django.contrib import messages
from django.utils.crypto import get_random_string
from .forms import AltaManualUsuarioForm
import secrets
import string
import random
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.urls import reverse_lazy


def home(request):
    return render(request, 'gestion_inmuebles/listaInmuebles.html')

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

            if user.is_superuser:
                token_existente = TokenVerificacion.objects.filter(usuario=user).first()
                if token_existente and not token_existente.expirado() and not token_existente.usado:
                    messages.error(request, 'Ya se envió un token válido. Esperá que expire o usalo.')
                    return redirect('verificar-token')

                # Generar nuevo token
                token = generar_token()
                
                TokenVerificacion.objects.update_or_create(
                    usuario=user,
                    defaults={'token': token, 'creado_en': timezone.now(), 'usado': False}
                )

                send_mail(
                    'Tu token de verificación',
                    f'Tu código es: {token}',
                    'no-reply@tuapp.com',
                    [user.email],
                    fail_silently=False,
                )
                
                request.session['pending_admin_id'] = user.id
                return redirect('verificar-token')
            else:
                login(request, user)
                return redirect('listaInmuebles')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'gestion_usuarios/login.html')

@login_required
def logout_usuario(request):
    logout(request)
    return redirect('listaInmuebles')

def es_empleado(user):
    return user.is_authenticated and user.is_staff
def es_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(es_empleado)
def panelEmp(request):
    return render(request, 'gestion_usuarios/panel-emp.html')



@user_passes_test(es_admin)
def panelAdmin(request):
    return render(request, 'gestion_usuarios/panel-admin.html')

@login_required
@user_passes_test(es_empleado)

def detalle_cliente(request, user_id):
    cliente = get_object_or_404(Usuario, id=user_id, is_staff=False, is_superuser=False)
    return render(request, 'gestion_usuarios/detalle-cliente.html', {'cliente': cliente})

@login_required
@user_passes_test(es_empleado)

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

def generar_token():
    return str(random.randint(100000, 999999))


def verificar_token(request):
    if request.method == 'POST':
        token_ingresado = request.POST.get('token')
        user_id = request.session.get('pending_admin_id')
        user = Usuario.objects.get(id=user_id)
        token_obj = TokenVerificacion.objects.filter(usuario=user, usado=False).first()

        if token_obj and not token_obj.expirado() and token_obj.token == token_ingresado:
            token_obj.usado = True
            token_obj.save()
            login(request, user)
            del request.session['pending_admin_id']
            return redirect('panel-admin')
        else:
            messages.error(request, 'Token incorrecto o expirado.')
    return render(request, 'gestion_usuarios/verificar-token.html')

@csrf_protect
def reenviar_token(request):
    user_id = request.session.get('pending_admin_id')
    if not user_id:
        messages.error(request, "Sesión no válida.")
        return redirect('login')

    usuario = get_object_or_404(Usuario, id=user_id)

    # Marcar el token anterior como usado
    TokenVerificacion.objects.filter(usuario=usuario, usado=False).update(usado=True)

    # Generar nuevo token
    nuevo_token = generar_token()
    TokenVerificacion.objects.update_or_create(
        usuario=usuario,
        defaults={'token': nuevo_token, 'creado_en': timezone.now(), 'usado': False}
    )

    send_mail(
        'Nuevo código de verificación',
        f'Tu nuevo código es: {nuevo_token}',
        'no-reply@tuapp.com',
        [usuario.email],
        fail_silently=False,
    )

    messages.success(request, "Se envió un nuevo código a tu correo.")
    return redirect('verificar-token')
@login_required
@user_passes_test(es_admin)
def alta_empleado(request):
    if request.method == 'POST':
        form = RegistroEmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado registrado correctamente.')
            return redirect('lista-empleados')
    else:
        form = RegistroEmpleadoForm()
    return render(request, 'gestion_usuarios/alta-empleado.html', {'form': form})

@login_required
@user_passes_test(es_admin)
def baja_empleado(request, user_id):
    empleado = get_object_or_404(Usuario, id=user_id, is_staff=True, is_superuser=False)
    
    if request.method == 'POST':
        empleado.is_active = False
        empleado.save()
        messages.success(request, 'Empleado dado de baja correctamente.')
        return redirect('lista-empleados')  # Redirigís correctamente luego de dar de baja
    
    return render(request, 'gestion_usuarios/baja-empleado.html', {'empleado': empleado})

@login_required
@user_passes_test(es_admin)
def habilitar_empleado(request, user_id):
    empleado = get_object_or_404(Usuario, id=user_id, is_staff=True, is_superuser=False)

    if request.method == 'POST':
        empleado.is_active = True
        empleado.save()
        messages.success(request, 'Empleado habilitado correctamente.')
        return redirect('lista-empleados')
    
    return render(request, 'gestion_usuarios/habilitar-empleado.html', {'empleado': empleado})

@login_required
@user_passes_test(es_admin)
def editar_empleado(request, user_id):
    empleado = get_object_or_404(Usuario, id=user_id, is_staff=True, is_superuser=False)
    if request.method == 'POST':
        form = EditarEmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado correctamente.')
            return redirect('detalle-empleado', user_id=empleado.id)
    else:
        form = EditarEmpleadoForm(instance=empleado)
    return render(request, 'gestion_usuarios/editar-empleado.html', {'form': form, 'empleado': empleado})

@login_required
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def deshabilitar_usuario(request, user_id):
    if request.method == 'POST':
        usuario = get_object_or_404(Usuario, id=user_id)
        if usuario.is_active:
            usuario.is_active = False
            usuario.save()
            messages.success(request, f'Cuenta de {usuario.username} deshabilitada correctamente.')
        else:
            messages.warning(request, f'La cuenta de {usuario.username} ya estaba deshabilitada.')
    return redirect('lista-clientes')  

@login_required
@user_passes_test(es_admin)
def habilitar_usuario(request, user_id):
    usuario = get_object_or_404(Usuario, id=user_id, is_superuser=False)

    if usuario.is_active:
        messages.warning(request, f'La cuenta de {usuario.username} ya está habilitada.')
        return redirect('lista-clientes')

    if request.method == 'POST':
        usuario.is_active = True
        usuario.save()
        messages.success(request, f'Cuenta de {usuario.username} habilitada correctamente.')
        return redirect('lista-clientes')

    return redirect('lista-clientes')

@login_required
@user_passes_test(es_empleado)
def generar_password_aleatoria(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))



@login_required
@user_passes_test(es_empleado)
def alta_manual_usuario(request):
    if request.method == 'POST':
        form = AltaManualUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            # Generar contraseña aleatoria
            contraseña_generada = secrets.token_urlsafe(8)
            usuario.set_password(contraseña_generada)
            usuario.save()

            # Enviar mail con la contraseña
            send_mail(
                subject='Bienvenido a Alquiler Express',
                message=f'Hola {usuario.first_name},\n\nTu cuenta fue creada exitosamente.\nTu Usuario es: {usuario.username}\n\nTu contraseña es: {contraseña_generada}\n\nPor favor, cambiala luego de ingresar.',
                from_email='tu-correo@ejemplo.com',
                recipient_list=[usuario.email],
                fail_silently=False,
            )

            messages.success(request, 'Usuario creado y notificado por correo.')
            form = AltaManualUsuarioForm()  # Limpio el formulario después de guardar
        else:
            messages.error(request, 'Por favor corregí los errores.')
    else:
        form = AltaManualUsuarioForm()
    
    return render(request, 'gestion_usuarios/alta_manual.html', {'form': form})


class MiPasswordChangeView(PasswordChangeView):
    template_name = 'gestion_usuarios/cambiar_password.html'
    success_url = reverse_lazy('perfil_usuario')  # o donde quieras redirigir

    def form_valid(self, form):
        messages.success(self.request, '¡Tu contraseña fue actualizada correctamente!')
        return super().form_valid(form)
