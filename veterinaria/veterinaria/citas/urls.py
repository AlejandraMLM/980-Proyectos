# citas/urls.py  (REEMPLAZA COMPLETO)
from django.urls import path
from . import views
from . import views_pdf

app_name = "citas"

urlpatterns = [
    # Carrito / agendado
    path("carrito/", views.ver_carrito, name="ver_carrito"),
    path("carrito/agregar/<int:servicio_id>/", views.agregar_al_carrito, name="agregar_al_carrito"),
    path("carrito/eliminar/<int:item_id>/", views.eliminar_del_carrito, name="eliminar_del_carrito"),
    path("carrito/actualizar/<int:item_id>/", views.actualizar_cantidad, name="actualizar_cantidad"),

    # Agendar
    path("agendar/", views.agendar_cita, name="agendar_cita"),  # <-- nombre que te falta
    # (opcional) alias por compatibilidad si en algún lado usas 'agendar'
    path("agendar-alias/", views.agendar_cita, name="agendar"),

    # Listado de citas del cliente
    path("mis/", views.mis_citas, name="mis_citas"),

    # PDFs
    path("pdf/mis/", views_pdf.pdf_cliente, name="pdf_mis"),
    path("pdf/vet/", views_pdf.pdf_veterinario, name="pdf_vet"),

    # Flujo de pago
    path('pago/<int:pago_id>/', views.pago_detalle, name='pago_detalle'),
    path('pago/<int:pago_id>/confirmar/', views.pago_confirmar, name='pago_confirmar'),

    # PDF: Boleta
     path("pdf/boleta/<int:pago_id>/", views_pdf.pdf_boleta, name="pdf_boleta"), 
]
