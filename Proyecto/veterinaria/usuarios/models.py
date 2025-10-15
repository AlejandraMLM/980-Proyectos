from django.contrib.auth.models import AbstractUser  # Importa el modelo de usuario abstracto de Django
from django.db import models                         # Importa los modelos de Django para base de datos

class Usuario(AbstractUser):
    # Definicion de opciones para el tipo de usuario
    TIPO_USUARIO = (
        ('cliente', 'Cliente'),       # Opcion para usuarios cliente
        ('admin', 'Administrador'),   # Opcion para usuarios administrador
    )
    
    # Campo para almacenar el tipo de usuario 
    tipo_usuario = models.CharField(max_length=10, choices=TIPO_USUARIO, default='cliente')
    
    # Campo para numero de telefono
    telefono = models.CharField(max_length=8, blank=False)
    
    # Campo para fecha de registro (se auto-completa al crear el usuario)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"