# veterinario/urls.py
from django.urls import path
from .views import (
    PanelVeterinarioView,
    PerfilVeterinarioUpdateView,
    CitasAsignadasListView,
    CitaMarcarCompletadaView,
    CitaMarcarCanceladaView,
    CitaHistorialCreateView,   # creación de nota clínica desde cita
)

app_name = "veterinario"

urlpatterns = [
    path("", PanelVeterinarioView.as_view(), name="panel"),
    path("perfil/", PerfilVeterinarioUpdateView.as_view(), name="perfil"),

    # Gestión de citas
    path("citas/", CitasAsignadasListView.as_view(), name="citas"),
    path("citas/<int:pk>/completar/", CitaMarcarCompletadaView.as_view(), name="cita_completar"),
    path("citas/<int:pk>/cancelar/", CitaMarcarCanceladaView.as_view(), name="cita_cancelar"),

    # Agregar historial clínico desde una cita específica
    path(
        "citas/<int:cita_id>/historial/nuevo/",
        CitaHistorialCreateView.as_view(),
        name="cita_historial_nuevo",
    ),
]
