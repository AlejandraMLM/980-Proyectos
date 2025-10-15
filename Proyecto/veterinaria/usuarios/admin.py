from django.contrib import admin                     # Importa el modulo de administracion de Django
from django.contrib.auth.admin import UserAdmin     # Importa la clase base para administrar usuarios
from .models import Usuario                         # Importa el modelo Usuario personalizado

# Registra el modelo Usuario en el panel de administracion con configuracion personalizada
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Configuracion de columnas visibles en la lista de usuarios
    list_display = ('username', 'email', 'tipo_usuario', 'is_staff', 'date_joined')
    
    # Configuracion de filtros disponibles en el panel lateral
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser')
    
    # Configuracion de campos en la edicion de usuarios 
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion adicional', {'fields': ('tipo_usuario', 'telefono')}),
    )
    
    # Configuracion de campos en la creacion de usuarios 
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informacion adicional', {'fields': ('tipo_usuario', 'telefono', 'email')}),
    )