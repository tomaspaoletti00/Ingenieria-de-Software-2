from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django.contrib.auth.models import User

class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'dni', 'telefono']
        labels = { 'username':'Nombre de Usuario', 'email':'Correo','password1':'Contraseña',
                  'password2':'Repetir Contraseña', 'first_name':"Nombre y Apellido",'dni':'DNI',
                  'telefono':'Nro de Telefono'}

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("El nombre no puede contener números.")
        return first_name



    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo ya está registrado.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 6:
            raise forms.ValidationError("La contraseña debe tener mínimo 6 caracteres.")
        return password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"
        
class EditarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'email', 'dni', 'telefono']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("El nombre no puede contener números.")
        return first_name


class RegistroEmpleadoForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'dni', 'telefono']
        labels = {
            'username': 'Nombre de Usuario',
            'email': 'Correo',
            'password1': 'Contraseña',
            'password2': 'Repetir Contraseña',
            'first_name': "Nombre y Apellido",
            'dni': 'DNI',
            'telefono': 'Nro de Telefono'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo ya está registrado.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 6:
            raise forms.ValidationError("La contraseña debe tener mínimo 6 caracteres.")
        return password
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("El nombre no puede contener números.")
        return first_name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Nombre de usuario"
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmar contraseña"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.is_superuser = False
        if commit:
            user.save()
        return user
    
class EditarEmpleadoForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'email', 'dni', 'telefono']
        labels = {
            'first_name': 'Nombre y Apellido',
            'email': 'Correo',
            'dni': 'DNI',
            'telefono': 'Teléfono'
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("El nombre no puede contener números.")
        return first_name
        
