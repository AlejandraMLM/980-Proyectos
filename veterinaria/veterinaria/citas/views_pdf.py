# citas/views_pdf.py
from io import BytesIO
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Cita, Pago
from servicios.models import Servicio

# PDF engine (xhtml2pdf)
try:
    from xhtml2pdf import pisa
except Exception:
    pisa = None


def _render_to_pdf(template_src, context):
    """
    Renderiza un template a PDF. Si falta xhtml2pdf, devuelve None y un error.
    """
    if pisa is None:
        return None, "Falta la librería xhtml2pdf. Instala con: pip install xhtml2pdf"

    html = render_to_string(template_src, context)
    result = BytesIO()
    pdf = pisa.CreatePDF(src=html, dest=result, encoding="UTF-8")
    if pdf.err:
        return None, "No se pudo generar el PDF. Revisa la plantilla o estilos."
    return result.getvalue(), None


def _filtrar_citas_base(request, base_qs):
    """
    Reutilizable para cliente/veterinario: aplica filtros GET.
    GET:
      - fecha_desde (YYYY-MM-DD)
      - fecha_hasta (YYYY-MM-DD)
      - estado [pendiente|confirmada|completada|cancelada]
      - servicio_id (int)
    """
    fecha_desde = request.GET.get("fecha_desde") or ""
    fecha_hasta = request.GET.get("fecha_hasta") or ""
    estado = request.GET.get("estado") or ""
    servicio_id = request.GET.get("servicio_id") or ""

    qs = base_qs.select_related("usuario", "servicio", "mascota", "veterinario").order_by("-fecha")

    if fecha_desde:
        qs = qs.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha__date__lte=fecha_hasta)
    if estado:
        qs = qs.filter(estado=estado)
    if servicio_id:
        qs = qs.filter(servicio_id=servicio_id)

    filtros = {
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
        "estado": estado,
        "servicio_id": servicio_id,
    }
    return qs, filtros


@login_required
def pdf_cliente(request):
    """
    PDF de citas del CLIENTE autenticado (solo sus propias citas).
    """
    base_qs = Cita.objects.filter(usuario=request.user)
    citas_qs, filtros = _filtrar_citas_base(request, base_qs)
    estados_choices = dict(Cita.ESTADOS)

    context = {
        "titulo": "Mis Citas",
        "quien": request.user.get_full_name() or request.user.username,
        "citas": citas_qs,
        "filtros": filtros,
        "servicios": Servicio.objects.all().order_by("nombre"),
        "filtro_estado_label": estados_choices.get(filtros["estado"], "Todos") if filtros.get("estado") else "Todos",
        "generado_en": timezone.localtime(timezone.now()),
    }

    pdf_bytes, error = _render_to_pdf("citas/reportes/citas_pdf.html", context)
    if error:
        messages.error(request, error)
        html = render_to_string("citas/reportes/citas_pdf.html", context)
        return HttpResponse(html)

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = 'attachment; filename="mis_citas.pdf"'
    return resp


@login_required
def pdf_veterinario(request):
    """
    PDF de citas del VETERINARIO autenticado (solo sus citas asignadas).
    """
    base_qs = Cita.objects.filter(veterinario=request.user)
    citas_qs, filtros = _filtrar_citas_base(request, base_qs)
    estados_choices = dict(Cita.ESTADOS)

    context = {
        "titulo": "Citas Asignadas",
        "quien": request.user.get_full_name() or request.user.username,
        "citas": citas_qs,
        "filtros": filtros,
        "servicios": Servicio.objects.all().order_by("nombre"),
        "filtro_estado_label": estados_choices.get(filtros["estado"], "Todos") if filtros.get("estado") else "Todos",
        "generado_en": timezone.localtime(timezone.now()),
    }

    pdf_bytes, error = _render_to_pdf("citas/reportes/citas_pdf.html", context)
    if error:
        messages.error(request, error)
        html = render_to_string("citas/reportes/citas_pdf.html", context)
        return HttpResponse(html)

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = 'attachment; filename="citas_asignadas.pdf"'
    return resp


# ===== PDF de Boleta de Pago (para el cliente dueño del pago) =====

@login_required
def pdf_boleta(request, pago_id):
    """
    Genera un PDF simple y compatible con xhtml2pdf para la boleta de pago.
    Evitamos CSS complejo/externo para que no salga en blanco.
    """
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    # Traemos las citas vinculadas a esta boleta (por FK en Cita: pago)
    citas = Cita.objects.select_related("servicio", "mascota").filter(pago=pago).order_by("fecha")

    context = {
        "pago": pago,
        "usuario": request.user,
        "citas": citas,
        "generado_en": timezone.localtime(timezone.now()),
    }

    pdf_bytes, error = _render_to_pdf("citas/reportes/boleta_pdf.html", context)
    if error:
        # Mostramos HTML para depurar si falla
        messages.error(request, error)
        html = render_to_string("citas/reportes/boleta_pdf.html", context)
        return HttpResponse(html)

    resp = HttpResponse(pdf_bytes, content_type="application/pdf")
    resp["Content-Disposition"] = f'attachment; filename="boleta_{pago.referencia}.pdf"'
    return resp
