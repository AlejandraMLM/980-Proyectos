# mascotas/views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.shortcuts import redirect, render, get_object_or_404
from django.http import Http404
from django.contrib import messages

from .models import Mascota, HistorialVeterinario
from .forms import (
    MascotaForm, InmunizacionFormSetFactory, HistorialFormSetFactory,
)

# Intentar usar NotaClinica/Cita (si existen) para mostrar en historial
HAS_NOTAS = False
try:
    from citas.models import NotaClinica, Cita  # type: ignore
    HAS_NOTAS = True
except Exception:
    pass


# ========= Mixins =========
class PropietarioQuerysetMixin(LoginRequiredMixin):
    def get_queryset(self):
        return Mascota.objects.filter(propietario=self.request.user)

class VetRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        u = self.request.user
        return getattr(u, "tipo_usuario", "") == "veterinario" or u.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "No tienes permisos para realizar esta acción.")
        return redirect("mascotas:listar")


# ========= Mascotas CRUD propietario =========
class MascotaListView(PropietarioQuerysetMixin, ListView):
    template_name = "mascotas/mascota_list.html"
    context_object_name = "mascotas"
    paginate_by = 10

class MascotaCreateView(LoginRequiredMixin, CreateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascotas/mascota_form.html"
    success_url = reverse_lazy("mascotas:listar")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        inmunizaciones = InmunizacionFormSetFactory(prefix="inmunizaciones")
        for i, f in enumerate(inmunizaciones.forms, start=1):
            f.fields["edad_anios"].initial = i

        historial = HistorialFormSetFactory(prefix="historial")
        return render(
            request,
            self.template_name,
            {"form": form, "inmunizaciones": inmunizaciones, "historial": historial},
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.form_class(request.POST, request.FILES, request=self.request)

        inmunizaciones = InmunizacionFormSetFactory(request.POST, prefix="inmunizaciones")
        historial = HistorialFormSetFactory(request.POST, request.FILES, prefix="historial")

        if form.is_valid() and inmunizaciones.is_valid() and historial.is_valid():
            mascota = form.save(commit=False)
            mascota.propietario = request.user
            mascota.save()
            self.object = mascota

            inmunizaciones.instance = mascota
            historial.instance = mascota
            inmunizaciones.save()
            historial.save()
            messages.success(request, "Mascota registrada correctamente.")
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {"form": form, "inmunizaciones": inmunizaciones, "historial": historial},
        )

class MascotaUpdateView(PropietarioQuerysetMixin, UpdateView):
    model = Mascota
    form_class = MascotaForm
    template_name = "mascotas/mascota_form.html"
    success_url = reverse_lazy("mascotas:listar")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        inmunizaciones = InmunizacionFormSetFactory(instance=self.object, prefix="inmunizaciones")
        existentes = set(self.object.inmunizaciones.values_list("edad_anios", flat=True))
        faltantes = [i for i in range(1, 16) if i not in existentes]

        iniciales = inmunizaciones.initial_form_count()
        total = inmunizaciones.total_form_count()
        idx = 0
        for pos in range(iniciales, total):
            if idx < len(faltantes):
                inmunizaciones.forms[pos].fields["edad_anios"].initial = faltantes[idx]
                idx += 1

        historial = HistorialFormSetFactory(instance=self.object, prefix="historial")
        return render(
            request,
            self.template_name,
            {"form": form, "inmunizaciones": inmunizaciones, "historial": historial},
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object, request=self.request)

        # Recalcular inmunizaciones desde formulario
        self.object.inmunizaciones.all().delete()

        inmunizaciones = InmunizacionFormSetFactory(request.POST, instance=self.object, prefix="inmunizaciones")
        historial = HistorialFormSetFactory(request.POST, request.FILES, instance=self.object, prefix="historial")

        if form.is_valid() and inmunizaciones.is_valid() and historial.is_valid():
            mascota = form.save()
            self.object = mascota

            inmunizaciones.save()
            historial.save()
            messages.success(request, "Mascota actualizada correctamente.")
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            {"form": form, "inmunizaciones": inmunizaciones, "historial": historial},
        )

class MascotaDeleteView(PropietarioQuerysetMixin, DeleteView):
    model = Mascota
    template_name = "mascotas/mascota_confirm_delete.html"
    success_url = reverse_lazy("mascotas:listar")

class MascotaDetailView(PropietarioQuerysetMixin, DetailView):
    model = Mascota
    template_name = "mascotas/mascota_detail.html"
    context_object_name = "mascota"


# ===== Historial clínico (lectura para propietario y veterinario) =====
class MascotaHistorialView(LoginRequiredMixin, DetailView):
    """
    Permite ver el historial si:
      - es el propietario de la mascota, o
      - es veterinario/staff.
    """
    model = Mascota
    template_name = "mascotas/historial.html"
    context_object_name = "mascota"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        u = request.user
        # Veterinario o staff
        if getattr(u, "tipo_usuario", "") == "veterinario" or u.is_staff:
            return super().dispatch(request, *args, **kwargs)
        # Propietario
        if self.object.propietario_id == u.id:
            return super().dispatch(request, *args, **kwargs)
        raise Http404("No tienes acceso a este historial.")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["registros"] = HistorialVeterinario.objects.filter(mascota=self.object).order_by("-fecha", "-id")
        if HAS_NOTAS:
            ctx["notas"] = NotaClinica.objects.filter(mascota=self.object) \
                          .select_related("veterinario", "cita").order_by("-fecha")
        else:
            ctx["notas"] = []
        ctx["es_veterinario"] = getattr(self.request.user, "tipo_usuario", "") == "veterinario" or self.request.user.is_staff
        return ctx


# ===== (Opcional) Atención del veterinario si luego lo usas aquí =====
# Puedes añadir tu AtencionCreateView aquí si decides moverlo al módulo mascotas.
