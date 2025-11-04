# citas/models.py
from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from servicios.models import Servicio
from mascotas.models import Mascota

User = get_user_model()


class Carrito(models.Model):
    usuario  = models.ForeignKey(User, on_delete=models.CASCADE)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['usuario', 'servicio']

    def __str__(self):
        return f"Carrito {self.usuario.username} - {self.servicio.nombre}"


class Pago(models.Model):
    METODOS = (
        ('transferencia', 'Depósito/Transferencia'),
    )
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('pendiente_verificacion', 'Pendiente de verificación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('vencido', 'Vencido'),
        ('cancelado', 'Cancelado'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pagos')
    metodo = models.CharField(max_length=30, choices=METODOS, default='transferencia')
    referencia = models.CharField(max_length=60, unique=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    estado = models.CharField(max_length=30, choices=ESTADOS, default='pendiente')
    fecha_limite = models.DateTimeField(null=True, blank=True)

    # Confirmación del banco (usuario sube comprobante)
    banco = models.CharField(max_length=60, blank=True)
    numero_boleta = models.CharField(max_length=60, blank=True)
    fecha_pago = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
    comprobante = models.FileField(upload_to='pagos/', null=True, blank=True)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-creado_en',)

    def __str__(self):
        return f"Pago {self.referencia} - {self.usuario}"

    @property
    def vencido(self):
        return bool(self.fecha_limite and timezone.now() > self.fecha_limite and self.estado in ('pendiente', 'pendiente_verificacion'))

    def marcar_vencido(self):
        """Marca pago como vencido y cancela sus citas asociadas que sigan abiertas."""
        if self.estado in ('pendiente', 'pendiente_verificacion'):
            self.estado = 'vencido'
            self.save(update_fields=['estado'])
            # cancelar citas aún abiertas
            for c in self.citas.all():
                if c.estado not in ('cancelada', 'completada'):
                    c.estado = 'cancelada'
                    c.actualizado_en = timezone.now()
                    c.save(update_fields=['estado', 'actualizado_en'])


class Cita(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )

    usuario   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citas_usuario')
    servicio  = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='citas_servicio')
    mascota   = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='citas', null=True, blank=True)

    # Veterinario asignado
    veterinario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas_asignadas',
        limit_choices_to={'tipo_usuario': 'veterinario'},
    )

    # Relación con pago (boleta)
    pago = models.ForeignKey(Pago, on_delete=models.SET_NULL, null=True, blank=True, related_name='citas')

    # Inicio / fin
    fecha     = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)

    estado    = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    notas     = models.TextField(blank=True)

    # Tracking
    actualizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas_actualizadas_por'
    )
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cita {self.id} - {self.usuario.username}"

    def _duracion_total(self):
        dur = getattr(self.servicio, 'duracion_minutos', None)
        if not dur:
            dur = getattr(self.servicio, 'duracion', 30)
        return timedelta(minutes=int(dur) + 5)

    def save(self, *args, **kwargs):
        # Calcular fecha_fin si no viene seteada
        if self.fecha and self.servicio and not self.fecha_fin:
            self.fecha_fin = self.fecha + self._duracion_total()
        super().save(*args, **kwargs)

    def puede_marcar_veterinario(self, user):
        if not user or not user.is_authenticated:
            return False
        return user.is_superuser or (self.veterinario_id == user.id)

    def marcar_completada(self, user):
        if not self.puede_marcar_veterinario(user):
            raise PermissionError("No puedes modificar esta cita.")
        if self.estado in ('cancelada', 'completada'):
            return
        self.estado = 'completada'
        self.actualizado_por = user
        self.actualizado_en = timezone.now()
        self.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])

    def marcar_cancelada(self, user):
        if not self.puede_marcar_veterinario(user):
            raise PermissionError("No puedes modificar esta cita.")
        if self.estado == 'completada':
            return
        self.estado = 'cancelada'
        self.actualizado_por = user
        self.actualizado_en = timezone.now()
        self.save(update_fields=['estado', 'actualizado_por', 'actualizado_en'])


class NotaClinica(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='notas_clinicas')
    cita = models.ForeignKey(Cita, on_delete=models.SET_NULL, null=True, blank=True, related_name='notas_clinicas')
    veterinario = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'tipo_usuario': 'veterinario'},
        related_name='notas_clinicas'
    )

    fecha = models.DateTimeField(auto_now_add=True)

    motivo = models.CharField(max_length=120, blank=True)
    diagnostico = models.TextField(blank=True)
    tratamiento = models.TextField(blank=True)
    medicamentos = models.TextField(blank=True)

    adjunto = models.FileField(upload_to='historial/', null=True, blank=True)

    class Meta:
        ordering = ('-fecha',)

    def __str__(self):
        return f"Nota clínica {self.id} - {self.mascota} ({self.fecha:%Y-%m-%d})"
