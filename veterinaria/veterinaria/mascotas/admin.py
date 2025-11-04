# mascotas/admin.py
from django.contrib import admin
from .models import Mascota, Inmunizacion, HistorialVeterinario

# Utilidad: devolver solo los nombres de campo que existen en el modelo
def existing_fields(model, names):
    model_field_names = {f.name for f in model._meta.get_fields()}
    return [n for n in names if n in model_field_names]

# ===== Inlines =====
class InmunizacionInline(admin.TabularInline):
    model = Inmunizacion
    extra = 0

class HistorialInline(admin.TabularInline):
    model = HistorialVeterinario
    extra = 0

# ===== Mascota =====
@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    pass

# Ajustes dinámicos según campos reales del modelo
MascotaAdmin.list_display = tuple(
    existing_fields(Mascota, ["id", "nombre", "especie", "propietario", "creado"])
) or ("id",)
MascotaAdmin.list_filter = tuple(existing_fields(Mascota, ["especie", "creado"]))
MascotaAdmin.search_fields = (
    "nombre",
    "propietario__username",
    "propietario__first_name",
    "propietario__last_name",
    "propietario__email",
)
if "propietario" in {f.name for f in Mascota._meta.get_fields()}:
    MascotaAdmin.autocomplete_fields = ("propietario",)
if "creado" in {f.name for f in Mascota._meta.get_fields()}:
    MascotaAdmin.date_hierarchy = "creado"
MascotaAdmin.ordering = ("-id",)
MascotaAdmin.list_select_related = tuple(
    f for f in ["propietario"] if f in {ff.name for ff in Mascota._meta.get_fields()}
)
MascotaAdmin.inlines = [InmunizacionInline, HistorialInline]

# ===== Inmunizacion =====
@admin.register(Inmunizacion)
class InmunizacionAdmin(admin.ModelAdmin):
    pass

# detecta posibles nombres típicos
inmu_candidates_display = existing_fields(
    Inmunizacion,
    ["id", "mascota", "tipo", "fecha", "proxima_fecha", "creado_en", "actualizado_en"],
)
InmunizacionAdmin.list_display = tuple(inmu_candidates_display) or ("id",)
InmunizacionAdmin.list_filter = tuple(
    existing_fields(Inmunizacion, ["tipo", "fecha", "proxima_fecha", "creado_en"])
)
InmunizacionAdmin.search_fields = (
    "mascota__nombre",
    "mascota__propietario__username",
    "mascota__propietario__first_name",
    "mascota__propietario__last_name",
)
if "mascota" in {f.name for f in Inmunizacion._meta.get_fields()}:
    InmunizacionAdmin.autocomplete_fields = ("mascota",)
# usa la primera fecha que exista como jerarquía
for dh in ["fecha", "proxima_fecha", "creado_en"]:
    if dh in {f.name for f in Inmunizacion._meta.get_fields()}:
        InmunizacionAdmin.date_hierarchy = dh
        break
InmunizacionAdmin.ordering = ("-id",)
InmunizacionAdmin.list_select_related = tuple(
    f for f in ["mascota", "mascota__propietario"]
    if f.split("__")[0] in {ff.name for ff in Inmunizacion._meta.get_fields()}
)

# ===== Historial Veterinario =====
@admin.register(HistorialVeterinario)
class HistorialVeterinarioAdmin(admin.ModelAdmin):
    pass

hist_candidates_display = existing_fields(
    HistorialVeterinario,
    ["id", "mascota", "titulo", "descripcion", "fecha", "creado_en", "actualizado_en"],
)
HistorialVeterinarioAdmin.list_display = tuple(hist_candidates_display) or ("id",)
HistorialVeterinarioAdmin.list_filter = tuple(
    existing_fields(HistorialVeterinario, ["fecha", "creado_en"])
)
HistorialVeterinarioAdmin.search_fields = (
    "titulo",
    "descripcion",
    "mascota__nombre",
    "mascota__propietario__username",
    "mascota__propietario__first_name",
    "mascota__propietario__last_name",
)
if "mascota" in {f.name for f in HistorialVeterinario._meta.get_fields()}:
    HistorialVeterinarioAdmin.autocomplete_fields = ("mascota",)
for dh in ["fecha", "creado_en"]:
    if dh in {f.name for f in HistorialVeterinario._meta.get_fields()}:
        HistorialVeterinarioAdmin.date_hierarchy = dh
        break
HistorialVeterinarioAdmin.ordering = ("-id",)
HistorialVeterinarioAdmin.list_select_related = tuple(
    f for f in ["mascota", "mascota__propietario"]
    if f.split("__")[0] in {ff.name for ff in HistorialVeterinario._meta.get_fields()}
)
