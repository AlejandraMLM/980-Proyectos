# mascotas/models.py
from django.conf import settings
from django.db import models
import os 

class Mascota(models.Model):
    ESPECIE_CHOICES = [
        ("perro", "Perro"),
        ("gato", "Gato"),
        ("ave", "Ave"),
        ("conejo", "Conejo"),
        ("reptil", "Reptil"),
        ("otro", "Otro"),
    ]
    SEXO_CHOICES = [("m", "Macho"), ("h", "Hembra"), ("u", "Desconocido")]

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mascotas"
    )

    # Datos de la mascota
    nombre = models.CharField(max_length=80)
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES)
    raza = models.CharField(max_length=80, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default="u")
    fecha_nacimiento = models.DateField(null=True, blank=True)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    color = models.CharField(max_length=60, blank=True)
    esterilizado = models.BooleanField(default=False)
    foto = models.ImageField(upload_to="mascotas/", blank=True, null=True)

    # NUEVOS: salud / atención
    alergias = models.TextField(blank=True)
    condiciones_actuales = models.TextField(blank=True)
    veterinario = models.CharField(max_length=120, blank=True)  # Vet habitual / clínica

    # Dirección
    departamento = models.CharField(max_length=100, blank=True)
    municipio = models.CharField(max_length=100, blank=True)
    zona = models.CharField(max_length=10, blank=True)
    direccion_completa = models.CharField(max_length=255, blank=True)

    # Contacto
    codigo_area = models.CharField(max_length=6, default="+502")
    telefono = models.CharField(max_length=20, blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        unique_together = [("propietario", "nombre")]
    def __str__(self):
        return f"{self.nombre} ({self.get_especie_display()})"


class Inmunizacion(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name="inmunizaciones")
    edad_anios = models.PositiveSmallIntegerField()  # 1..15

    rabia = models.BooleanField(default=False)
    dhpp = models.BooleanField(default=False)
    lyme = models.BooleanField(default=False)
    bordetella = models.BooleanField(default=False)
    lepto = models.BooleanField(default=False)
    influenza = models.BooleanField(default=False)

    class Meta:
        unique_together = [("mascota", "edad_anios")]
        ordering = ["edad_anios"]
    def __str__(self):
        return f"{self.mascota.nombre} - {self.edad_anios} año(s)"


class HistorialVeterinario(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name="historiales")
    fecha = models.DateField()
    descripcion = models.CharField(max_length=200, blank=True)
    veterinario = models.CharField(max_length=120, blank=True)
    diagnostico = models.CharField(max_length=200, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]
    
    def upload_to(instance, filename):
        # Guarda en veterinaria/media/mascotas/
        mascotas_dir = os.path.join('mascotas', 'fotos')
        os.makedirs(os.path.join(settings.MEDIA_ROOT, mascotas_dir), exist_ok=True)
        return os.path.join(mascotas_dir, filename)
    
    foto = models.ImageField(upload_to=upload_to, blank=True, null=True)
    
    def __str__(self):
        return f"{self.mascota.nombre} - {self.fecha}"

    