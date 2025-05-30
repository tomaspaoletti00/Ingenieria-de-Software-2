from django.forms import ModelForm, NumberInput
from django import forms
from .models import Inmueble, Departamento, Casa, Local, Cochera

class CustomClearableFileInput(forms.ClearableFileInput):
    initial_text = ''      # texto para "Currently" (Actualmente)
    input_text = 'Cambiar' # texto para el botón "Change"
    clear_checkbox_label = 'Limpiar imagen'  # el texto que ya estás seteando

class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        fields = '__all__'
        exclude = ['activo']
        widgets = {
            'imagen': CustomClearableFileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'imagen' in self.fields:
            self.fields['imagen'].widget.clear_checkbox_label = "Limpiar imagen"

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a cero.')
        return precio


#   Formularios para Departamento, Casa, Local y Cochera
#   Tecnicamente se puede borrar el de arriba pero por las dudas no toco nada


class FormularioDepartamento(InmuebleForm):
    class Meta:
        model = Departamento    
        fields = '__all__'
        exclude = ['activo']
        

class FormularioCasa(InmuebleForm):
    class Meta(InmuebleForm):
        model = Casa
        fields = '__all__'
        exclude = ['activo']


class FormularioLocal(InmuebleForm):    
    class Meta(InmuebleForm):
        model = Local
        fields = '__all__'
        exclude = ['activo']

class FormularioCochera(InmuebleForm):
    class Meta(InmuebleForm):
        model = Cochera
        fields = '__all__'
        exclude = ['activo']


