from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django.contrib.auth.models import User

class RegistroUsuarioForm(UserCreationForm):
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
        if password and len(password) < 6:
            raise forms.ValidationError("La contraseña debe tener mínimo 6 caracteres.")
        return password

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if not password2:
            raise forms.ValidationError("Por favor, confirme la contraseña.")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        if password2 and len(password2) < 6:
            raise forms.ValidationError("La contraseña debe tener mínimo 6 caracteres.")

        return password2

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
        
class AltaManualUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'dni', 'telefono']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'dni': forms.NumberInput(attrs={'placeholder': 'DNI'}),
            'telefono': forms.NumberInput(attrs={'placeholder': 'Teléfono'}),
            'username': forms.TextInput(attrs={'placeholder': 'Nombre de usuario'}),
        }

        def clean_email(self):
            email = self.cleaned_data['email']
            if Usuario.objects.filter(email=email).exists():
                raise forms.ValidationError('El correo ya está registrado.')
            return email
 
        def clean_username(self):
             username = self.cleaned_data['username']
             if Usuario.objects.filter(username=username).exists():
                 raise forms.ValidationError('Ya existe un usuario con este nombre.')
             return username
        
from django.contrib.auth.forms import PasswordChangeForm
from django import forms

class MiPasswordChangeForm(PasswordChangeForm):
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError("La contraseña actual es incorrecta. Intentá de nuevo.")
        return old_password
    
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < 6:
            raise forms.ValidationError("La nueva contraseña debe tener al menos 6 caracteres.")
        return password
    
    def clean_new_password2(self):
        password = self.cleaned_data.get('new_password2')
        if len(password) < 6:
            raise forms.ValidationError("La nueva contraseña debe tener al menos 6 caracteres.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data
