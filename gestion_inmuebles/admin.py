from django.contrib import admin
from .models import Cochera
from .models import Departamento
from .models import Casa
from .models import Local
# Register your models here.

admin.site.register(Departamento)
admin.site.register(Casa)
admin.site.register(Cochera)
admin.site.register(Local)