from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower
from django.conf import settings

class Usuario(AbstractUser):
    # Definicion de opciones para el tipo de usuario
    TIPO_USUARIO = (
        ('cliente', 'Cliente'),
        ('veterinario', 'Veterinario'),
        ('admin', 'Administrador'),
    )

    # unicidad a nivel de BD
    email = models.EmailField("email address", unique=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('email'),
                name='uniq_usuario_email_ci'
            )
        ]

    # NUEVO: Campos de nombre y apellido
    first_name = models.CharField("nombre", max_length=150, blank=False)
    last_name = models.CharField("apellido", max_length=150, blank=False)
    
    # Campo para almacenar el tipo de usuario 
    tipo_usuario = models.CharField(max_length=15, choices=TIPO_USUARIO, default='cliente')
    
    # Campo para numero de telefono
    telefono = models.CharField(max_length=8, blank=False)
    
    # Campo para fecha de registro (se auto-completa al crear el usuario)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"
    
    def get_full_name(self):
        """Retorna el nombre completo (nombre + apellido)"""
        return f"{self.first_name} {self.last_name}".strip()
    
    # ========= PERFIL DE VETERINARIO =========
class VeterinarioPerfil(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil_veterinario')
    colegiado = models.CharField(max_length=50, blank=True)
    especialidades = models.CharField(max_length=255, blank=True, help_text="Ej.: Cirugía, Dermatología")
    bio = models.TextField(blank=True)
    foto = models.ImageField(upload_to='veterinarios/', blank=True, null=True)

    # ¿acepta citas actualmente?
    disponible = models.BooleanField(default=True)

    # Servicios que atiende (opcional, para filtrar agenda)
   
    servicios = models.ManyToManyField('servicios.Servicio', blank=True, related_name='veterinarios')

    class Meta:
        verbose_name = "Perfil de Veterinario"
        verbose_name_plural = "Perfiles de Veterinario"

    def __str__(self):
        return f"Perfil Vet: {self.usuario.get_full_name()}"
