from django.urls import path    # Importa la funcion path para definir rutas URL
from . import views             # Importa las vistas del modulo actual

app_name = 'citas'  # URLs de citas

urlpatterns = [
    path('carrito/agregar/<int:servicio_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),    # Agregar al carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),                                            # Ver carrito
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),   # Eliminar del carrito
    path('carrito/actualizar/<int:item_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),   # Actualizar cantidad
    path('agendar/', views.agendar_cita, name='agendar_cita'),                                          # Agendar cita
]