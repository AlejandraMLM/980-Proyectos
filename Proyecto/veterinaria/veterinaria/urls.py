from django.contrib import admin                       # Módulo de administración de Django
from django.urls import path, include                  # Funciones para definir rutas URL
from django.contrib.auth import views as auth_views    # Vistas de autenticación 
from servicios.views import home                       # Importa la vista 'home' desde la aplicación 'servicios'

# Definición de los patrones de URL del proyecto
urlpatterns = [
    
     # PANEL DE ADMINISTRACIÓN DE DJANGO
     path('admin/', admin.site.urls),
    
     # PÁGINA DE INICIO
     path('', home, name='home'),
    
     # LOGIN DE USUARIOS
     path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
     # LOGOUT DE USUARIOS
     path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
     # APLICACIÓN DE USUARIOS
     path('usuarios/', include('usuarios.urls')),
    
     # APLICACIÓN DE SERVICIOS
     path('servicios/', include('servicios.urls')),
    
     # PANEL DE ADMINISTRACIÓN PERSONALIZADO
     path('administrador/', include('administrador.urls')),
    
     # SISTEMA DE RECUPERACIÓN DE CONTRASEÑA
     path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), 
         name='password_reset'),
    
     # Ruta que confirma que se envió el email de recuperación
     path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), 
         name='password_reset_done'),
    
     # Ruta para confirmar la nueva contraseña (contiene token de seguridad)
     path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    
     # Ruta final que confirma que la contraseña fue cambiada exitosamente
     path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), 
         name='password_reset_complete'),
     # URLs de citas
    path('citas/', include('citas.urls')),       
]