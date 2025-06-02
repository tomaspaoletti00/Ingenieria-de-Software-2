from django import forms
from .models import Inmueble, Departamento, Casa, Local, Cochera

TIEMPO_GENERAL = [
    ('Por_semana', 'Por semana'),
    ('Por_mes', 'Por mes'),
    ('Por_noche', 'Por noche'),
]

TIEMPO_COCHERA = [
    ('Por_hora', 'Por hora'),
]

class CustomClearableFileInput(forms.ClearableFileInput):
    initial_text = ''
    input_text = 'Cambiar'
    clear_checkbox_label = 'Limpiar imagen'


class InmuebleForm(forms.ModelForm):
    class Meta:
        model = Inmueble
        # Nota: no uses 'fields' y 'exclude' juntos, usa solo uno
        exclude = ['activo']
        widgets = {
            'imagen': CustomClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'imagen' in self.fields:
            self.fields['imagen'].widget.clear_checkbox_label = "Limpiar imagen"
        self.fields['superficie'].label = "Superficie (m²)"

    def clean_superficie(self):
        superficie = self.cleaned_data.get('superficie')
        if superficie is not None and superficie <= 0:
            raise forms.ValidationError('La superficie debe ser mayor a cero.')
        return superficie
    
    def clean_precio(self):
        superficie = self.cleaned_data.get('precio')
        if superficie is not None and superficie <= 0:
            raise forms.ValidationError('El precio debe ser mayor a cero.')
        return superficie


# =============== Formularios personalizados ====================

class FormularioDepartamento(InmuebleForm):
    class Meta(InmuebleForm.Meta):
        model = Departamento
        # Asegurate que hereda bien el exclude y widgets

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tiempo'].choices = TIEMPO_GENERAL
        self.fields['banios'].label = "Baños"



class FormularioCasa(InmuebleForm):
    class Meta(InmuebleForm.Meta):
        model = Casa

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tiempo'].choices = TIEMPO_GENERAL
        self.fields['banios'].label = "Baños"



class FormularioLocal(InmuebleForm):
    class Meta(InmuebleForm.Meta):
        model = Local
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tiempo'].choices = TIEMPO_GENERAL
        self.fields['banios'].label = "Baños"
        self.fields['frente'].label = "Frente (m²)"
        self.fields['fondo'].label = "Fondo (m²)"


    def clean_frente(self):
        frente = self.cleaned_data.get('frente')
        if frente is not None and frente <= 0:
            raise forms.ValidationError('El frente debe ser mayor a cero.')
        return frente

    def clean_fondo(self):
        fondo = self.cleaned_data.get('fondo')
        if fondo is not None and fondo <= 0:
            raise forms.ValidationError('El fondo debe ser mayor a cero.')
        return fondo


class FormularioCochera(InmuebleForm):
    class Meta(InmuebleForm.Meta):
        model = Cochera

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tiempo'].choices = TIEMPO_COCHERA
        self.fields['largo_plaza'].label = "Largo de la plaza (m²)"
        self.fields['ancho_plaza'].label = "Ancho de la plaza (m²)"

    def clean_largo_plaza(self):
        largo = self.cleaned_data.get('largo_plaza')
        if largo is not None and largo <= 0:
            raise forms.ValidationError('El largo de la plaza debe ser mayor a cero.')
        return largo

    def clean_plazas(self):
        plazas = self.cleaned_data.get('plazas')
        if plazas is not None and plazas <= 0:
            raise forms.ValidationError('Debe haber al menos una plaza.')
        return plazas
