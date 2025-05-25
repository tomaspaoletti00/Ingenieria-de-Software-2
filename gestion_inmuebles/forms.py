from django.forms import ModelForm, NumberInput
from .models import Inmueble, Departamento, Casa, Local, Cochera

class InmuebleForm(ModelForm):       
        
        class Meta:
            model = Inmueble
            fields = '__all__'
            exclude = ['activo']

        def clean(self):
            cleaned_data = super().clean()

            campos_a_validar = ['precio']  # Agregá los campos que quieras validar

            for campo in campos_a_validar:
                valor = cleaned_data.get(campo)
                if valor is not None and valor <= 0:
                    self.add_error(campo, f'El campo {campo} debe ser mayor a cero.')

            return cleaned_data


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


