from django.urls import path  # Importa la funcion path para definir rutas URL
from . import views           # Importa las vistas del modulo actual

# Definicion de los patrones de URL para la aplicacion usuarios
urlpatterns = [
    path('registro/', views.registro, name='registro'),  # Ruta para el formulario de registro de usuarios
]