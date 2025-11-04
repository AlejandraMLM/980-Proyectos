from django.shortcuts import render
from .models import Servicio

def home(request):
    servicios = Servicio.objects.filter(disponible=True)
    return render(request, 'home.html', {'servicios': servicios})