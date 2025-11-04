from django import forms
from django.utils import timezone
from datetime import time, timedelta
from django.contrib.auth import get_user_model

from .models import Cita
from mascotas.models import Mascota

# Horarios de atención: 0=Lunes ... 6=Domingo
HORARIO = {
    0: (time(8, 0),  time(19, 0)),  # L
    1: (time(8, 0),  time(19, 0)),  # M
    2: (time(8, 0),  time(19, 0)),  # X
    3: (time(8, 0),  time(19, 0)),  # J
    4: (time(8, 0),  time(19, 0)),  # V
    5: (time(9, 0),  time(15, 0)),  # S
    6: (time(9, 0),  time(15, 0)),  # D
}


def _duracion_total(servicio) -> timedelta:
    """
    Duración real del servicio + 5 min de buffer.
    Soporta servicio.duracion o servicio.duracion_minutos; default 30.
    """
    minutes = (
        getattr(servicio, "duracion_minutos", None)
        or getattr(servicio, "duracion", None)
        or 30
    )
    try:
        minutes = int(minutes)
    except Exception:
        minutes = 30
    return timedelta(minutes=minutes + 5)


class CitaForm(forms.ModelForm):
    """
    Form de agendamiento.
    - Fecha/hora por servicio: campos dt_<servicio_id> (DateTimeField).
    - Veterinario por servicio: campos vet_<servicio_id> (ModelChoiceField).
    """

    # Campos de facturación (no-model)
    factura_nombre        = forms.CharField(label="Nombre / Razón social", required=True)
    factura_nit           = forms.CharField(label="NIT", required=True)
    factura_direccion     = forms.CharField(label="Dirección", required=True)
    factura_departamento  = forms.CharField(label="Departamento", required=True)
    factura_municipio     = forms.CharField(label="Municipio", required=True)
    factura_email         = forms.EmailField(label="Correo para factura", required=True)
    factura_telefono      = forms.CharField(label="Teléfono", required=False)

    class Meta:
        model = Cita
        # OJO: ya NO incluimos "fecha" aquí; ahora es por servicio
        fields = ["mascota", "notas"]
        widgets = {
            "mascota": forms.Select(attrs={"class": "form-control"}),
            "notas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        """
        kwargs esperados:
          - user: para filtrar mascotas del dueño
          - servicios: lista/qs de Servicio (o Carrito.servicio)
        """
        self.user = kwargs.pop("user", None)
        servicios = kwargs.pop("servicios", None)
        super().__init__(*args, **kwargs)

        # filtrar mascotas por propietario (si no es staff)
        if self.user is not None and not getattr(self.user, "is_staff", False):
            self.fields["mascota"].queryset = Mascota.objects.filter(propietario=self.user)
        else:
            self.fields["mascota"].queryset = Mascota.objects.all()

        # clases para facturación
        for n in [
            "factura_nombre", "factura_nit", "factura_direccion", "factura_departamento",
            "factura_municipio", "factura_email", "factura_telefono",
        ]:
            self.fields[n].widget.attrs.setdefault("class", "form-control")

        # --- Normalizar lista de servicios únicos ---
        self._servicios = []  # lista ordenada de objetos Servicio
        if servicios:
            vistos = set()
            for obj in servicios:
                s = getattr(obj, "servicio", obj)  # soporta Carrito o Servicio directo
                if s and s.id not in vistos:
                    self._servicios.append(s)
                    vistos.add(s.id)

        # --- Campos dinámicos por servicio ---
        User = get_user_model()
        for s in self._servicios:
            # Veterinario para el servicio s
            self.fields[f"vet_{s.id}"] = forms.ModelChoiceField(
                queryset=User.objects.filter(
                    tipo_usuario="veterinario",
                    perfil_veterinario__disponible=True,
                    perfil_veterinario__servicios=s,
                )
                .order_by("first_name", "last_name", "username")
                .distinct(),
                required=True,
                empty_label="Selecciona un veterinario",
                label=f"Veterinario para {s.nombre}",
                widget=forms.Select(attrs={"class": "form-select"}),
            )

            # Fecha/hora para el servicio s
            self.fields[f"dt_{s.id}"] = forms.DateTimeField(
                required=True,
                label=f"Fecha y hora para {s.nombre}",
                widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            )

    # --- Validaciones ---
    def _validar_horario(self, dt):
        wd = dt.weekday()
        inicio, fin = HORARIO.get(wd)
        if not (inicio <= dt.time() <= fin):
            raise forms.ValidationError("La hora está fuera del horario de atención.")

    def clean(self):
        cleaned = super().clean()

        # Construir itinerario preliminar y validar por-veterinario
        self._itinerary = []  # [(servicio, vet, start, end)]
        field_errors = {}

        # 1) Validar cada par (vet, dt) y traslapes con citas existentes
        for s in self._servicios:
            vet = cleaned.get(f"vet_{s.id}")
            dt  = cleaned.get(f"dt_{s.id}")

            if not vet or not dt:
                # Django ya marcará requerido; continuamos
                continue

            # dentro de horario
            try:
                self._validar_horario(dt)
            except forms.ValidationError as e:
                field_errors[f"dt_{s.id}"] = e.messages[0]
                continue

            start = dt
            end   = dt + _duracion_total(s)

            # Traslape con citas existentes de ese veterinario
            # (ignoramos canceladas)
            existe = Cita.objects.filter(
                veterinario=vet,
                fecha__lt=end,
                fecha_fin__gt=start,
            ).exclude(estado="cancelada").exists()

            if existe:
                field_errors[f"dt_{s.id}"] = "Ya existe una cita en ese rango para el veterinario seleccionado."
            else:
                self._itinerary.append((s, vet, start, end))

        # 2) Validar traslapes entre los servicios elegidos si comparten veterinario
        #    (por si el usuario pone horas que se pisan)
        for i in range(len(self._itinerary)):
            si, vi, ai, bi = self._itinerary[i]
            for j in range(i + 1, len(self._itinerary)):
                sj, vj, aj, bj = self._itinerary[j]
                if vi == vj and (ai < bj and bi > aj):
                    # Se traslapan en la elección
                    field_errors[f"dt_{si.id}"] = "Se traslapa con otra hora elegida para el mismo veterinario."
                    field_errors[f"dt_{sj.id}"] = "Se traslapa con otra hora elegida para el mismo veterinario."

        # Reportar errores por campo si los hay
        for fname, msg in field_errors.items():
            self.add_error(fname, msg)

        return cleaned

    # Entrega la lista de (servicio, veterinario, inicio, fin) ordenada por inicio
    def get_itinerary(self):
        if not hasattr(self, "_itinerary"):
            return []
        return sorted(self._itinerary, key=lambda t: t[2])
