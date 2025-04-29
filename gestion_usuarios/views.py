from django.shortcuts import render
from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm

from django.contrib.auth import authenticate, login
from django.contrib import messages

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
            return redirect('home')  # redirigí a la vista que quieras como home
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'gestion_usuarios/login.html')