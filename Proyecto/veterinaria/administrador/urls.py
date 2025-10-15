from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.panel_principal, name='inicio'),
    path('panel/', views.panel_principal, name='panel'),
    path('servicios/', views.gestion_servicios, name='gestion_servicios'),
    path('servicios/agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('servicios/editar/<int:servicio_id>/', views.editar_servicio, name='editar_servicio'),
    path('servicios/eliminar/<int:servicio_id>/', views.eliminar_servicio, name='eliminar_servicio'),
]