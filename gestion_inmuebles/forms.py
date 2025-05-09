from django.forms import ModelForm
from .models import Inmueble, Departamento, Casa, Local, Cochera

class InmuebleForm(ModelForm):
    class Meta:
        model = Inmueble
        fields = '__all__'

#   Formularios para Departamento, Casa, Local y Cochera
#   Tecnicamente se puede borrar el de arriba pero por las dudas no toco nada

class FormularioDepartamento(ModelForm):
    class Meta:
        model = Departamento
        fields = '__all__'

class FormularioCasa(ModelForm):
    class Meta:
        model = Casa
        fields = '__all__'

class FormularioLocal(ModelForm):
    class Meta:
        model = Local
        fields = '__all__'

class FormularioCochera(ModelForm):
    class Meta:
        model = Cochera
        fields = '__all__'