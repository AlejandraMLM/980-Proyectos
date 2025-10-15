from django.db import models

class Servicio(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del servicio")
    descripcion = models.TextField(verbose_name="Descripción")
    precio = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Precio")
    disponible = models.BooleanField(default=True, verbose_name="Disponible")
    duracion = models.IntegerField(help_text="Duración en minutos", verbose_name="Duración (min)")
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True, verbose_name="Imagen")
    
    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"
    
    def __str__(self):
        return self.nombre