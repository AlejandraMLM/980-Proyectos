from django.contrib import admin
from .models import Servicio  # Solo importar Servicio, no Cita

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'duracion', 'disponible']
    list_filter = ['disponible']
    search_fields = ['nombre']