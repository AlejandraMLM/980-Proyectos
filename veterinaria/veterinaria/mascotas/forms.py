# mascotas/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Mascota, Inmunizacion, HistorialVeterinario

# ==== (1) Form Mascota (igual) ====
class MascotaForm(forms.ModelForm):
    propietario_nombre = forms.CharField(label="Nombre del propietario", required=False, disabled=True,
                                         widget=forms.TextInput(attrs={'class': 'form-control'}))
    propietario_apellido = forms.CharField(label="Apellido del propietario", required=False, disabled=True,
                                           widget=forms.TextInput(attrs={'class': 'form-control'}))
    propietario_email = forms.EmailField(label="Correo del propietario", required=False, disabled=True,
                                         widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Mascota
        fields = [
            "propietario_nombre", "propietario_apellido", "propietario_email",
            "nombre", "especie", "raza", "sexo", "fecha_nacimiento",
            "peso_kg", "color", "esterilizado", "foto",
            "alergias", "condiciones_actuales", "veterinario",
            "departamento", "municipio", "zona", "direccion_completa",
            "codigo_area", "telefono",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "alergias": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "condiciones_actuales": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono de contacto'}),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.FileInput)):
                field.widget.attrs.setdefault("class", "form-control")

        if request and request.user.is_authenticated:
            u = request.user
            self.fields["propietario_nombre"].initial = getattr(u, "first_name", "") or "No especificado"
            self.fields["propietario_apellido"].initial = getattr(u, "last_name", "") or "No especificado"
            self.fields["propietario_email"].initial = getattr(u, "email", "") or "No especificado"

        if not self.instance.pk and not self.fields["codigo_area"].initial:
            self.fields["codigo_area"].initial = "+502"

    def clean_telefono(self):
        tel = (self.cleaned_data.get("telefono") or "").strip()
        if tel and len(tel) < 8:
            raise forms.ValidationError("El teléfono debe tener al menos 8 dígitos")
        return tel

# ==== (2) Formsets fijos (igual) ====
class InmunizacionForm(forms.ModelForm):
    class Meta:
        model = Inmunizacion
        fields = ["edad_anios", "rabia", "dhpp", "lyme", "bordetella", "lepto", "influenza"]
        widgets = {"edad_anios": forms.HiddenInput()}

class HistorialVeterinarioForm(forms.ModelForm):
    class Meta:
        model = HistorialVeterinario
        fields = ["fecha", "descripcion", "veterinario", "diagnostico", "foto"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "descripcion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Motivo / Resumen"}),
            "veterinario": forms.TextInput(attrs={"class": "form-control"}),
            "diagnostico": forms.TextInput(attrs={"class": "form-control"}),
            "foto": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

InmunizacionFormSetFactory = inlineformset_factory(
    Mascota, Inmunizacion, form=InmunizacionForm,
    extra=15, can_delete=False, min_num=15, max_num=15, validate_min=True, validate_max=True
)

HistorialFormSetFactory = inlineformset_factory(
    Mascota, HistorialVeterinario, form=HistorialVeterinarioForm,
    extra=1, can_delete=True
)

# ==== (3) Form para la atención del veterinario ====
# Si existe citas.NotaClinica, usamos ese modelo (tiene motivo/diagnostico/tratamiento/medicamentos/adjunto)
NotaClinicaForm = None
try:
    from citas.models import NotaClinica  # type: ignore

    class NotaClinicaFormBase(forms.ModelForm):
        class Meta:
            model = NotaClinica
            fields = ["fecha", "motivo", "diagnostico", "tratamiento", "medicamentos", "adjunto"]
            widgets = {
                "fecha": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
                "motivo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Motivo de consulta / Resumen"}),
                "diagnostico": forms.TextInput(attrs={"class": "form-control"}),
                "tratamiento": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
                "medicamentos": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
                "adjunto": forms.ClearableFileInput(attrs={"class": "form-control"}),
            }

    NotaClinicaForm = NotaClinicaFormBase
except Exception:
    # Fallback: usamos HistorialVeterinario para guardar algo
    class NotaClinicaForm(forms.ModelForm):
        """Respaldo si no existe citas.NotaClinica."""
        class Meta:
            model = HistorialVeterinario
            fields = ["fecha", "descripcion", "diagnostico", "foto"]
            widgets = {
                "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
                "descripcion": forms.TextInput(attrs={"class": "form-control", "placeholder": "Motivo / Resumen"}),
                "diagnostico": forms.TextInput(attrs={"class": "form-control"}),
                "foto": forms.ClearableFileInput(attrs={"class": "form-control"}),
            }
