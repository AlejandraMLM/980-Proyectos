from django.contrib import admin                     # Importa el modulo de administracion de Django
from django.contrib.auth.admin import UserAdmin      # Importa la clase base para administrar usuarios
from .models import Usuario, VeterinarioPerfil       # Importa el modelo Usuario personalizado y el perfil de veterinario

# Inline para editar el perfil de veterinario directamente en el usuario
class VeterinarioPerfilInline(admin.StackedInline):
    model = VeterinarioPerfil
    can_delete = False
    fk_name = 'usuario'
    extra = 0
    fields = ('colegiado', 'especialidades', 'bio', 'foto', 'disponible', 'servicios')

# Registra el modelo Usuario en el panel de administracion con configuracion personalizada
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Configuracion de columnas visibles en la lista de usuarios
    list_display = ('username', 'email', 'first_name', 'last_name', 'tipo_usuario', 'is_staff', 'date_joined')
    
    # Configuracion de filtros disponibles en el panel lateral
    list_filter = ('tipo_usuario', 'is_staff', 'is_superuser', 'is_active')
    
    # Búsqueda rápida
    search_fields = ('username', 'email', 'first_name', 'last_name')

    # Configuracion de campos en la edicion de usuarios 
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion adicional', {'fields': ('tipo_usuario', 'telefono')}),
    )
    
    # Configuracion de campos en la creacion de usuarios 
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informacion adicional', {'fields': ('tipo_usuario', 'telefono', 'email')}),
    )

    # Mostrar inline del Perfil de Veterinario
    inlines = [VeterinarioPerfilInline]

# Admin del perfil de veterinario (listado/filtros/busqueda)
@admin.register(VeterinarioPerfil)
class VeterinarioPerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'colegiado', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'colegiado')
