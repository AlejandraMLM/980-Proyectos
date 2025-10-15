from django.contrib import admin
from .models import Carrito, Cita

@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'cantidad', 'agregado_en')
    list_filter = ('agregado_en',)
    search_fields = ('usuario__username', 'servicio__nombre')
    date_hierarchy = 'agregado_en'

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'servicio', 'fecha', 'estado', 'creado_en')
    list_filter = ('estado', 'fecha')
    search_fields = ('usuario__username', 'servicio__nombre')
    date_hierarchy = 'fecha'