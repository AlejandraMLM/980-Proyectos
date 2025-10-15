from django.db import models                    # Importa los modelos de Django
from django.contrib.auth import get_user_model  # Funcion para obtener el modelo de usuario
from servicios.models import Servicio            # Importa el modelo Servicio

class Cita(models.Model):
    # Opciones para los estados de la cita
    ESTADOS = (
        ('pendiente', 'Pendiente'),      # Estado inicial de la cita
        ('confirmada', 'Confirmada'),    # Cita confirmada por el administrador
        ('completada', 'Completada'),    # Cita finalizada exitosamente
        ('cancelada', 'Cancelada'),      # Cita cancelada
    )
    
    # Relacion con el usuario que agenda la cita
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='citas_usuario')
    
    # Relacion con el servicio solicitado
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='citas_servicio')
    
    # Fecha y hora programada para la cita
    fecha = models.DateTimeField()  # Fecha y hora de la cita
    
    # Estado actual de la cita 
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')  
    
    # Notas adicionales sobre la cita 
    notas = models.TextField(blank=True)  # Observaciones
    
    # Fecha de creacion automatica
    creado_en = models.DateTimeField(auto_now_add=True)  
    
    def __str__(self):
        
        return f"Cita {self.id} - {self.usuario.username}"  # Formato: Cita 1 - nombre_usuario

class Carrito(models.Model):
    # Relacion con el usuario dueño del carrito
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  
    
    # Relacion con el servicio agregado al carrito
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)  
    
    # Cantidad del servicio (por defecto 1)
    cantidad = models.IntegerField(default=1)  
    
    # Fecha de agregado automatica
    agregado_en = models.DateTimeField(auto_now_add=True)  # Se establece automaticamente al agregar
    
    class Meta:
        # Evita duplicados: un usuario no puede tener el mismo servicio multiple veces
        unique_together = ['usuario', 'servicio']  
        
    def __str__(self):
        
        return f"Carrito {self.usuario.username} - {self.servicio.nombre}"  # Formato: Carrito usuario - servicio