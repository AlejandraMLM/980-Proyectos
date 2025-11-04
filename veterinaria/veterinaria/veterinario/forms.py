# --- Agregar debajo de tus imports existentes ---
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from citas.models import Cita
from mascotas.models import HistorialVeterinario
from .forms import HistorialNotaForm
from usuarios.decorators import role_required
from django.utils.decorators import method_decorator
from django.contrib import messages

@method_decorator(role_required('veterinario'), name='dispatch')
class HistorialCreateView(View):
    """
    Crear una nota clínica para la mascota de una cita.
    Solo el veterinario asignado (o superuser) puede crearla.
    """
    template_name = "veterinario/historial_form.html"

    def get(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)
        if not (request.user.is_superuser or cita.veterinario_id == request.user.id):
            messages.error(request, "No tienes permiso para agregar historial a esta cita.")
            return redirect("veterinario:citas")

        if not cita.mascota_id:
            messages.error(request, "La cita no tiene mascota asociada.")
            return redirect("veterinario:citas")

        form = HistorialNotaForm()
        return render(request, self.template_name, {"form": form, "cita": cita})

    def post(self, request, pk):
        cita = get_object_or_404(Cita, pk=pk)
        if not (request.user.is_superuser or cita.veterinario_id == request.user.id):
            messages.error(request, "No tienes permiso para agregar historial a esta cita.")
            return redirect("veterinario:citas")

        form = HistorialNotaForm(request.POST, request.FILES)
        if form.is_valid():
            nota: HistorialVeterinario = form.save(commit=False)
            nota.mascota = cita.mascota
            nota.veterinario = request.user
            nota.save()
            messages.success(request, "Nota clínica agregada al historial.")
            # Redirige al historial visible por el cliente
            return redirect("mascotas:historial", pk=cita.mascota_id)

        return render(request, self.template_name, {"form": form, "cita": cita})
