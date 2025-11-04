# mascotas/urls.py
from django.urls import path
from .views import (
    MascotaListView,
    MascotaCreateView,
    MascotaUpdateView,
    MascotaDeleteView,
    MascotaDetailView,
    MascotaHistorialView,
)

app_name = "mascotas"

urlpatterns = [
    path("", MascotaListView.as_view(), name="listar"),
    path("nueva/", MascotaCreateView.as_view(), name="crear"),
    path("<int:pk>/", MascotaDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", MascotaUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", MascotaDeleteView.as_view(), name="eliminar"),
    path("<int:pk>/historial/", MascotaHistorialView.as_view(), name="historial"),
]
