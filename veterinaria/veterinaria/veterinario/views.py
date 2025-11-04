# veterinario/views.py
from django.views.generic import TemplateView, UpdateView, ListView, View
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages
from usuarios.decorators import role_required
from django.utils.decorators import method_decorator
from django.utils import timezone

from usuarios.models import VeterinarioPerfil
from citas.models import Cita
from mascotas.models import HistorialVeterinario


# =========================
# Panel y Perfil
# =========================

@method_decorator(role_required('veterinario'), name='dispatch')
class PanelVeterinarioView(TemplateView):
    template_name = "veterinario/panel.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        perfil, _ = VeterinarioPerfil.objects.get_or_create(usuario=user)
        ctx['perfil'] = perfil
        return ctx


@method_decorator(role_required('veterinario'), name='dispatch')
class PerfilVeterinarioUpdateView(UpdateView):
    model = VeterinarioPerfil
    fields = ['colegiado', 'especialidades', 'bio', 'foto', 'disponible', 'servicios']
    template_name = "veterinario/perfil_form.html"
    success_url = reverse_lazy('veterinario:panel')

    def get_object(self, queryset=None):
        perfil, _ = VeterinarioPerfil.objects.get_or_create(usuario=self.request.user)
        return perfil

    def form_valid(self, form):
        messages.success(self.request, "Perfil de veterinario actualizado.")
        return super().form_valid(form)


# =========================
# Citas: listado y acciones
# =========================

@method_decorator(role_required('veterinario'), name='dispatch')
class CitasAsignadasListView(ListView):
    template_name = "veterinario/citas_asignadas.html"
    model = Cita
    paginate_by = 20

    def get_queryset(self):
        qs = (Cita.objects
              .select_related('usuario', 'mascota', 'servicio', 'veterinario')
              .filter(veterinario=self.request.user)
              .order_by('-fecha'))
        estado = self.request.GET.get('estado')
        if estado:
            qs = qs.filter(estado=estado)
        return qs


@method_decorator(role_required('veterinario'), name='dispatch')
class CitaMarcarCompletadaView(View):
    def post(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)
        try:
            cita.marcar_completada(request.user)
            messages.success(request, f"Cita #{cita.id} marcada como COMPLETADA.")
        except Exception as e:
            messages.error(request, f"No se pudo completar la cita: {e}")
        next_url = request.POST.get('next') or reverse_lazy('veterinario:citas')
        return redirect(next_url)


@method_decorator(role_required('veterinario'), name='dispatch')
class CitaMarcarCanceladaView(View):
    def post(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)
        try:
            cita.marcar_cancelada(request.user)
            messages.success(request, f"Cita #{cita.id} marcada como CANCELADA.")
        except Exception as e:
            messages.error(request, f"No se pudo cancelar la cita: {e}")
        next_url = request.POST.get('next') or reverse_lazy('veterinario:citas')
        return redirect(next_url)


# =========================
# Crear historial desde cita
# =========================

def _clip_to_field(text: str, model, field_name: str) -> str:
    """
    Corta el texto al tamaño máximo definido en el modelo para evitar
    errores de 'value too long for type character varying(...)'.
    """
    if text is None:
        return ""
    try:
        limit = model._meta.get_field(field_name).max_length
    except Exception:
        limit = None
    if limit:
        return text[:limit]
    return text


@method_decorator(role_required('veterinario'), name='dispatch')
class CitaHistorialCreateView(View):
    """
    FORM dedicado para registrar una atención desde la cita.
    Guarda en tu modelo HistorialVeterinario SIN migraciones:
      - motivo -> descripcion (recortado a max_length)
      - diagnostico -> diagnostico (recortado a max_length)
      - tratamiento/medicamentos -> se agregan al final de 'descripcion' (y se recorta)
      - veterinario (CharField) -> nombre completo del usuario (recortado a max_length)
      - fecha -> hoy
    """
    template_name = "veterinario/cita_historial_form.html"

    def get(self, request, cita_id):
        cita = get_object_or_404(Cita, pk=cita_id)

        # Seguridad: solo el vet asignado o superuser
        if not (request.user.is_superuser or cita.veterinario_id == request.user.id):
            messages.error(request, "No puedes agregar historial a esta cita.")
            return redirect('veterinario:citas')

        context = {
            "cita": cita,
            "mascota": cita.mascota,
        }
        return render(request, self.template_name, context)

    def post(self, request, cita_id):
        cita = get_object_or_404(Cita, pk=cita_id)
        if not (request.user.is_superuser or cita.veterinario_id == request.user.id):
            messages.error(request, "No puedes agregar historial a esta cita.")
            return redirect('veterinario:citas')

        motivo        = (request.POST.get("motivo") or "").strip()
        diagnostico   = (request.POST.get("diagnostico") or "").strip()
        tratamiento   = (request.POST.get("tratamiento") or "").strip()
        medicamentos  = (request.POST.get("medicamentos") or "").strip()
        adjunto       = request.FILES.get("adjunto")

        if not (motivo or diagnostico or tratamiento or medicamentos or adjunto):
            messages.error(request, "Completa al menos un campo de la nota clínica.")
            return redirect('veterinario:cita_historial_nuevo', cita_id=cita.id)

        # Construir descripción con extras y recortar a límites del modelo
        descripcion = motivo
        extras = []
        if tratamiento:
            extras.append(f"Tratamiento/Exámenes: {tratamiento}")
        if medicamentos:
            extras.append(f"Medicamentos: {medicamentos}")
        if extras:
            descripcion = (descripcion + ("\n" if descripcion else "")) + "\n".join(extras)

        descripcion = _clip_to_field(descripcion, HistorialVeterinario, "descripcion")
        diagnostico = _clip_to_field(diagnostico, HistorialVeterinario, "diagnostico")

        vet_name = (request.user.get_full_name() or request.user.username or "").strip()
        vet_name = _clip_to_field(vet_name, HistorialVeterinario, "veterinario")

        # Guardar registro seguro
        HistorialVeterinario.objects.create(
            mascota=cita.mascota,
            fecha=timezone.now().date(),
            descripcion=descripcion,
            veterinario=vet_name,
            diagnostico=diagnostico,
            foto=adjunto,
        )

        messages.success(request, "Historial clínico agregado correctamente.")
        # Opcional: marcar la cita como completada automáticamente
        try:
            cita.marcar_completada(request.user)
        except Exception:
            pass

        return redirect('mascotas:historial', pk=cita.mascota_id)
