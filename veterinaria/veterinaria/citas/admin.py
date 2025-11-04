# citas/admin.py
from django.contrib import admin

# Importaciones seguras (evitan ImportError si el modelo no existe)
Carrito = Cita = Pago = NotaClinica = None
try:
    from .models import Carrito as _Carrito
    Carrito = _Carrito
except Exception:
    pass

try:
    from .models import Cita as _Cita
    Cita = _Cita
except Exception:
    pass

try:
    from .models import Pago as _Pago
    Pago = _Pago
except Exception:
    pass

try:
    from .models import NotaClinica as _NotaClinica
    NotaClinica = _NotaClinica
except Exception:
    pass


# ===== Admin Carrito (opcional si existe) =====
if Carrito:
    @admin.register(Carrito)
    class CarritoAdmin(admin.ModelAdmin):
        list_display = ('usuario', 'servicio', 'cantidad', 'agregado_en')
        list_filter = ('agregado_en',)
        search_fields = ('usuario__username', 'servicio__nombre')
        date_hierarchy = 'agregado_en'


# ===== Admin Pago (opcional si existe) =====
if Pago and Cita:
    class CitaInline(admin.TabularInline):
        model = Cita
        fields = ('id', 'fecha', 'servicio', 'mascota', 'estado')
        readonly_fields = ('id', 'fecha', 'servicio', 'mascota', 'estado')
        extra = 0
        can_delete = False
        show_change_link = True

if Pago:
    @admin.register(Pago)
    class PagoAdmin(admin.ModelAdmin):
        list_display = ('referencia', 'usuario', 'monto_total', 'estado', 'fecha_limite', 'creado_en')
        list_filter = ('estado', 'metodo', 'fecha_limite', 'creado_en')
        search_fields = ('referencia', 'usuario__username', 'usuario__email')
        readonly_fields = ('referencia', 'usuario', 'monto_total', 'fecha_limite', 'creado_en', 'actualizado_en')
        date_hierarchy = 'creado_en'
        ordering = ('-creado_en',)
        inlines = [CitaInline] if (Cita and Pago) else []
        actions = ['aprobar_pagos', 'rechazar_pagos', 'marcar_vencidos']

        @admin.action(description="Aprobar pagos seleccionados")
        def aprobar_pagos(self, request, queryset):
            if not Cita:
                self.message_user(request, "No se pudo actualizar citas porque el modelo Cita no está disponible.")
                return
            count = 0
            for p in queryset:
                if p.estado in ('pendiente', 'pendiente_verificacion'):
                    p.estado = 'aprobado'
                    p.save(update_fields=['estado'])
                    for c in p.citas.all():
                        if c.estado in ('pendiente', 'confirmada'):
                            c.estado = 'confirmada'
                            c.save(update_fields=['estado'])
                    count += 1
            self.message_user(request, f"{count} pago(s) aprobados.")

        @admin.action(description="Rechazar pagos seleccionados")
        def rechazar_pagos(self, request, queryset):
            if not Cita:
                self.message_user(request, "No se pudo actualizar citas porque el modelo Cita no está disponible.")
                return
            count = 0
            for p in queryset:
                if p.estado in ('pendiente', 'pendiente_verificacion'):
                    p.estado = 'rechazado'
                    p.save(update_fields=['estado'])
                    for c in p.citas.all():
                        if c.estado not in ('cancelada', 'completada'):
                            c.estado = 'cancelada'
                            c.save(update_fields=['estado'])
                    count += 1
            self.message_user(request, f"{count} pago(s) rechazados.")

        @admin.action(description="Marcar vencidos (y cancelar citas)")
        def marcar_vencidos(self, request, queryset):
            count = 0
            for p in queryset:
                if p.estado in ('pendiente', 'pendiente_verificacion'):
                    try:
                        p.marcar_vencido()
                        count += 1
                    except Exception:
                        pass
            self.message_user(request, f"{count} pago(s) marcados como vencidos y citas canceladas.")


# ===== Admin Cita (opcional si existe) =====
if Cita:
    @admin.register(Cita)
    class CitaAdmin(admin.ModelAdmin):
        list_display = (
            'id', 'fecha', 'fecha_fin', 'estado',
            'servicio', 'mascota', 'usuario', 'veterinario',
            'pago', 'actualizado_por', 'actualizado_en', 'creado_en'
        )
        list_filter = ('estado', 'servicio', 'veterinario', 'fecha')
        search_fields = (
            'usuario__username', 'usuario__first_name', 'usuario__last_name',
            'mascota__nombre', 'servicio__nombre', 'pago__referencia'
        )
        date_hierarchy = 'fecha'
        ordering = ('-fecha',)
        autocomplete_fields = tuple(f for f in ('usuario', 'mascota', 'servicio', 'veterinario', 'actualizado_por', 'pago') if f)
        readonly_fields = ('fecha_fin', 'actualizado_por', 'actualizado_en', 'creado_en')
        list_select_related = ('usuario', 'mascota', 'servicio', 'veterinario', 'actualizado_por', 'pago')
        actions = ['accion_marcar_completada', 'accion_marcar_cancelada']

        @admin.action(description="Marcar como COMPLETADA (seleccionadas)")
        def accion_marcar_completada(self, request, queryset):
            count = 0
            for cita in queryset:
                try:
                    cita.marcar_completada(request.user)
                    count += 1
                except Exception:
                    pass
            self.message_user(request, f"{count} cita(s) marcadas como COMPLETADA.")

        @admin.action(description="Marcar como CANCELADA (seleccionadas)")
        def accion_marcar_cancelada(self, request, queryset):
            count = 0
            for cita in queryset:
                try:
                    cita.marcar_cancelada(request.user)
                    count += 1
                except Exception:
                    pass
            self.message_user(request, f"{count} cita(s) marcadas como CANCELADA.")


# ===== Admin NotaClinica (opcional si existe) =====
if NotaClinica:
    @admin.register(NotaClinica)
    class NotaClinicaAdmin(admin.ModelAdmin):
        list_display = ('id', 'mascota', 'veterinario', 'cita', 'fecha')
        list_filter = ('fecha', 'veterinario')
        search_fields = ('mascota__nombre', 'veterinario__username')
        date_hierarchy = 'fecha'
