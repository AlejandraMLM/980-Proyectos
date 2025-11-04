from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q, Count
from io import BytesIO

from servicios.models import Servicio
from citas.models import Cita
from usuarios.models import Usuario
from .forms import ServicioForm

# PDF
try:
    from xhtml2pdf import pisa
except Exception:
    pisa = None  # Permitirá mostrar error elegante si falta la librería


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "No tienes permisos de administrador")
            return redirect('login')
    return wrapper


@login_required
@admin_required
def panel_principal(request):
    """Panel principal con datos reales de la base de datos"""
    try:
        total_servicios = Servicio.objects.count()
        total_citas = Cita.objects.count()
        total_usuarios = Usuario.objects.count()
        citas_pendientes = Cita.objects.filter(estado='pendiente').count()

        context = {
            'total_servicios': total_servicios,
            'total_citas': total_citas,
            'total_usuarios': total_usuarios,
            'citas_pendientes': citas_pendientes,
            'hide_breadcrumb': True,
        }
        return render(request, 'administrador/panel.html', context)
    except Exception as e:
        messages.error(request, f"Error al cargar el panel de administracion: {str(e)}")
        return redirect('home')


@login_required
@admin_required
def gestion_servicios(request):
    """Gestion de servicios"""
    try:
        servicios = Servicio.objects.all().order_by('-id')
        return render(request, 'administrador/gestion_servicios.html', {'servicios': servicios})
    except Exception as e:
        messages.error(request, f"Error al cargar los servicios: {str(e)}")
        return render(request, 'administrador/gestion_servicios.html', {'servicios': []})


@login_required
@admin_required
def agregar_servicio(request):
    """Agregar nuevo servicio"""
    if request.method == 'POST':
        form = ServicioForm(request.POST, request.FILES)
        if form.is_valid():
            servicio = form.save()
            messages.success(request, f'Servicio "{servicio.nombre}" agregado exitosamente')
            return redirect('administrador:gestion_servicios')
        else:
            messages.error(request, 'Error en el formulario. Por favor corrige los errores.')
    else:
        form = ServicioForm()
    return render(request, 'administrador/agregar_servicio.html', {'form': form})


@login_required
@admin_required
def editar_servicio(request, servicio_id):
    """Editar un servicio existente"""
    try:
        servicio = get_object_or_404(Servicio, id=servicio_id)
        if request.method == 'POST':
            form = ServicioForm(request.POST, request.FILES, instance=servicio)
            if form.is_valid():
                servicio_editado = form.save()
                messages.success(request, f'Servicio "{servicio_editado.nombre}" actualizado exitosamente')
                return redirect('administrador:gestion_servicios')
            else:
                messages.error(request, 'Error en el formulario. Por favor corrige los errores.')
        else:
            form = ServicioForm(instance=servicio)

        return render(request, 'administrador/editar_servicio.html', {'form': form, 'servicio': servicio})
    except Exception as e:
        messages.error(request, f"Error al editar el servicio: {str(e)}")
        return redirect('administrador:gestion_servicios')


@login_required
@admin_required
def eliminar_servicio(request, servicio_id):
    """Eliminar un servicio"""
    try:
        servicio = get_object_or_404(Servicio, id=servicio_id)
        nombre_servicio = servicio.nombre
        servicio.delete()
        messages.success(request, f'Servicio "{nombre_servicio}" eliminado exitosamente')
    except Exception as e:
        messages.error(request, f"Error al eliminar el servicio: {str(e)}")
    return redirect('administrador:gestion_servicios')


# ---------------------------
# Reporte de Citas (HTML + PDF)
# ---------------------------

def _filtrar_citas(request):
    """
    Aplica filtros de GET a la queryset de Cita.
    Filtros:
      - fecha_desde=YYYY-MM-DD
      - fecha_hasta=YYYY-MM-DD
      - estado=[pendiente|confirmada|completada|cancelada]
      - servicio_id=<int>
      - usuario=<texto en username|nombre|email>
    """
    qs = Cita.objects.select_related('usuario', 'servicio', 'mascota').order_by('-fecha')

    fecha_desde = request.GET.get('fecha_desde') or ''
    fecha_hasta = request.GET.get('fecha_hasta') or ''
    estado = request.GET.get('estado') or ''
    servicio_id = request.GET.get('servicio_id') or ''
    usuario_q = request.GET.get('usuario') or ''

    if fecha_desde:
        qs = qs.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        qs = qs.filter(fecha__date__lte=fecha_hasta)
    if estado:
        qs = qs.filter(estado=estado)
    if servicio_id:
        qs = qs.filter(servicio_id=servicio_id)
    if usuario_q:
        qs = qs.filter(
            Q(usuario__username__icontains=usuario_q) |
            Q(usuario__first_name__icontains=usuario_q) |
            Q(usuario__last_name__icontains=usuario_q) |
            Q(usuario__email__icontains=usuario_q)
        )

    return qs, {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'estado': estado,
        'servicio_id': servicio_id,
        'usuario': usuario_q
    }


@admin_required
def reporte_citas(request):
    """Vista HTML con tabla y filtros"""
    citas_qs, filtros = _filtrar_citas(request)

    # Mapa de estados: {'pendiente': 'Pendiente', ...}
    estados_choices = dict(Cita.ESTADOS)

    # Resumen por estado con etiquetas listas para plantilla
    resumen_qs = citas_qs.values('estado').annotate(total=Count('id')).order_by()
    resumen = [
        {
            'estado_code': r['estado'],
            'estado_label': estados_choices.get(r['estado'], r['estado']),
            'total': r['total'],
        }
        for r in resumen_qs
    ]

    # Etiqueta “bonita” del estado seleccionado en filtros
    filtro_estado_label = estados_choices.get(filtros['estado'], 'Todos') if filtros.get('estado') else 'Todos'

    context = {
        'citas': citas_qs,
        'filtros': filtros,
        'estados_choices': estados_choices,     # <- usar en selects
        'servicios': Servicio.objects.all().order_by('nombre'),
        'resumen': resumen,                     # <- ya viene con label
        'filtro_estado_label': filtro_estado_label,
        'ahora': timezone.localtime(timezone.now()),
    }
    return render(request, 'administrador/reportes.html', context)


def _render_to_pdf(template_src, context_dict):
    """Renderiza un template a PDF usando xhtml2pdf"""
    if pisa is None:
        # xhtml2pdf no instalado
        html = render_to_string(template_src, context_dict)
        resp = HttpResponse(html)
        resp.status_code = 500
        return resp, "Falta la librería xhtml2pdf. Instala con: pip install xhtml2pdf"

    html = render_to_string(template_src, context_dict)
    result = BytesIO()
    pdf = pisa.CreatePDF(src=html, dest=result, encoding='UTF-8')
    if pdf.err:
        return None, "No se pudo generar el PDF. Revisa la plantilla o estilos."
    return result.getvalue(), None


@login_required
@admin_required
def reporte_citas_pdf(request):
    """Genera un PDF con la misma data filtrada que la vista HTML"""
    citas_qs, filtros = _filtrar_citas(request)
    estados_choices = dict(Cita.ESTADOS)
    filtro_estado_label = estados_choices.get(filtros['estado'], 'Todos') if filtros.get('estado') else 'Todos'

    context = {
        'citas': citas_qs,
        'filtros': filtros,
        'servicios': Servicio.objects.all().order_by('nombre'),
        'filtro_estado_label': filtro_estado_label,  # <- usar en template PDF
        'generado_en': timezone.localtime(timezone.now()),
    }

    pdf_bytes, error = _render_to_pdf('administrador/reportes_pdf.html', context)
    if error:
        messages.error(request, error)
        return render(request, 'administrador/reportes.html', {
            **context,
            'estados_choices': estados_choices,
            'ahora': timezone.localtime(timezone.now()),
            'resumen': [],
        })

    filename = "reporte_citas.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response