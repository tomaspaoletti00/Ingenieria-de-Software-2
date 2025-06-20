from django.shortcuts import render

# Create your views here.

def menu_estadisticas(request):
    return render(request, 'gestion_estadisticas/menu-estadisticas.html')