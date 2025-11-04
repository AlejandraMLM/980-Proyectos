# citas/views.py
from decimal import Decimal, ROUND_HALF_UP
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Carrito, Cita, Pago
from servicios.models import Servicio

IVA = Decimal("0.12")  # Guatemala


# ========= util de filtros (igual a views_pdf) =========
def _filtrar_citas_base(request, base_qs):
    """
    Aplica filtros GET comunes:
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


# ========= Carrito =========
@login_required
def agregar_al_carrito(request, servicio_id):
    try:
        servicio = get_object_or_404(Servicio, id=servicio_id)
        if not servicio.disponible:
            messages.error(request, "Este servicio no está disponible actualmente")
            return redirect("home")

        item, created = Carrito.objects.get_or_create(
            usuario=request.user,
            servicio=servicio,
            defaults={"cantidad": 1},
        )
        if not created:
            item.cantidad += 1
            item.save()

        messages.success(request, f'"{servicio.nombre}" agregado al carrito')
        return redirect("home")
    except Exception as e:
        messages.error(request, f"Error al agregar al carrito: {str(e)}")
        return redirect("home")


@login_required
def ver_carrito(request):
    try:
        carrito_items = Carrito.objects.filter(usuario=request.user).select_related("servicio")
        subtotal = sum((it.servicio.precio * it.cantidad) for it in carrito_items)
        iva = (Decimal(subtotal) * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (Decimal(subtotal) + iva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return render(
            request,
            "citas/carrito.html",
            {"carrito_items": carrito_items, "subtotal": subtotal, "iva": iva, "total": total},
        )
    except Exception as e:
        messages.error(request, f"Error al cargar el carrito: {str(e)}")
        return render(request, "citas/carrito.html", {"carrito_items": [], "subtotal": 0, "iva": 0, "total": 0})


@login_required
def eliminar_del_carrito(request, item_id):
    try:
        item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
        nombre = item.servicio.nombre
        item.delete()
        messages.success(request, f'"{nombre}" eliminado del carrito')
        return redirect("citas:ver_carrito")
    except Exception as e:
        messages.error(request, f"Error al eliminar del carrito: {str(e)}")
        return redirect("citas:ver_carrito")


@login_required
def actualizar_cantidad(request, item_id):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        try:
            item = get_object_or_404(Carrito, id=item_id, usuario=request.user)
            nueva = int(request.POST.get("cantidad", 1))
            if nueva <= 0:
                return JsonResponse({"success": False, "error": "Cantidad inválida"})
            item.cantidad = nueva
            item.save()

            carrito_items = Carrito.objects.filter(usuario=request.user).select_related("servicio")
            subtotal = sum((it.servicio.precio * it.cantidad) for it in carrito_items)
            iva = (Decimal(subtotal) * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            total = (Decimal(subtotal) + iva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            return JsonResponse(
                {
                    "success": True,
                    "subtotal_item": float(item.servicio.precio * item.cantidad),
                    "subtotal": float(subtotal),
                    "iva": float(iva),
                    "total": float(total),
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Método no permitido"})


# ========= Agendar (con boleta/pago simulado) =========
@login_required
def agendar_cita(request):
    """
    Agendamiento desde carrito con selección de veterinario y fecha/hora por servicio.
    Luego de agendar, se crea un Pago (boleta) y se redirige a la página de pago.
    """
    carrito_items = Carrito.objects.filter(usuario=request.user).select_related("servicio")
    if not carrito_items.exists():
        messages.error(request, 'No hay servicios en el carrito para agendar.')
        return redirect('citas:ver_carrito')

    servicios_carrito = [ci.servicio for ci in carrito_items]

    # Totales para mostrar en el formulario (y reutilizar en el correo)
    subtotal = sum((it.servicio.precio * it.cantidad) for it in carrito_items)
    iva = (Decimal(subtotal) * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = (Decimal(subtotal) + iva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    from .forms import CitaForm  # evitar import circular al cargar el módulo

    if request.method == 'POST':
        form = CitaForm(request.POST, user=request.user, servicios=servicios_carrito)
        if form.is_valid():
            try:
                mascota = form.cleaned_data.get('mascota')
                notas = form.cleaned_data.get('notas')

                # Datos de facturación (ya existentes en tu form)
                fac_nombre = form.cleaned_data.get('factura_nombre')
                fac_nit    = form.cleaned_data.get('factura_nit')
                fac_dir    = form.cleaned_data.get('factura_direccion')
                fac_depto  = form.cleaned_data.get('factura_departamento')
                fac_muni   = form.cleaned_data.get('factura_municipio')
                fac_email  = form.cleaned_data.get('factura_email')
                fac_tel    = form.cleaned_data.get('factura_telefono')

                itinerary = form.get_itinerary()  # [(srv, vet, ini, fin), ...]
                citas_creadas = []
                for srv, vet, ini, fin in itinerary:
                    c = Cita(
                        usuario=request.user,
                        servicio=srv,
                        mascota=mascota,
                        veterinario=vet,
                        fecha=ini,
                        fecha_fin=fin,
                        estado='pendiente',
                        notas=notas,
                    )
                    c.save()
                    citas_creadas.append(c)

                # Filas para la tabla de importes (precio * cantidad)
                rows = []
                for it in carrito_items:
                    rows.append({
                        "descripcion": it.servicio.nombre,
                        "precio": it.servicio.precio,
                        "cantidad": it.cantidad,
                        "importe": it.servicio.precio * it.cantidad,
                    })

                # Envío del comprobante por correo
                html = render_to_string(
                    "citas/factura_email.html",
                    {
                        "usuario": request.user,
                        "mascota": mascota,
                        "citas": citas_creadas,
                        "rows": rows,
                        "subtotal": subtotal,
                        "iva": iva,
                        "total": total,
                        "fac_nombre": fac_nombre,
                        "fac_nit": fac_nit,
                        "fac_dir": fac_dir,
                        "fac_depto": fac_depto,
                        "fac_muni": fac_muni,
                        "fac_email": fac_email,
                        "fac_tel": fac_tel,
                    },
                )

                send_mail(
                    subject="Comprobante de Cita - MyVetPet",
                    message="Tu cliente de correo no soporta HTML.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email],
                    html_message=html,
                    fail_silently=False,
                )

                # ===== Crear boleta de pago =====
                consecutivo = str(uuid.uuid4())[:4].upper()
                referencia = f"MV-{request.user.id}-{timezone.now():%Y%m%d}-{consecutivo}"
                fecha_limite = timezone.now() + timedelta(hours=48)

                pago = Pago.objects.create(
                    usuario=request.user,
                    metodo='transferencia',
                    estado='pendiente',
                    referencia=referencia,
                    monto_total=Decimal(total),
                    fecha_limite=fecha_limite,
                )

                # Vincular citas al pago
                for c in citas_creadas:
                    c.pago = pago
                    c.save(update_fields=['pago'])

                # Limpiar carrito
                carrito_items.delete()

                messages.success(request, '¡Citas agendadas! Generamos tu boleta de pago.')
                return redirect('citas:pago_detalle', pago_id=pago.id)
            except Exception as e:
                messages.error(request, f'Error al agendar: {str(e)}')
    else:
        form = CitaForm(user=request.user, servicios=servicios_carrito)

    return render(
        request,
        'citas/agendar_cita.html',
        {
            'form': form,
            'carrito_items': carrito_items,
            'servicios_carrito': servicios_carrito,
            'subtotal': subtotal,
            'iva': iva,
            'total': total,
        }
    )


# ========= Pago simulado =========
@login_required
def pago_detalle(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)
    # Si venció, marcar y cancelar
    if pago.estado in ('pendiente', 'pendiente_verificacion') and pago.vencido:
        pago.marcar_vencido()
        messages.error(request, "La boleta venció. Tus citas fueron canceladas.")
    return render(request, "citas/pago_instrucciones.html", {"pago": pago})


@login_required
def pago_confirmar(request, pago_id):
    pago = get_object_or_404(Pago, id=pago_id, usuario=request.user)

    if pago.estado in ('aprobado', 'rechazado', 'vencido', 'cancelado'):
        messages.info(request, f"El pago está en estado: {pago.get_estado_display()}.")
        return redirect('citas:pago_detalle', pago_id=pago.id)

    if request.method == "POST":
        banco = (request.POST.get("banco") or "").strip()
        numero_boleta = (request.POST.get("numero_boleta") or "").strip()
        fecha_pago = request.POST.get("fecha_pago") or None
        notas = (request.POST.get("notas") or "").strip()
        comprobante = request.FILES.get("comprobante")

        if not banco or not numero_boleta or not fecha_pago or not comprobante:
            messages.error(request, "Completa todos los campos y adjunta el comprobante.")
            return redirect('citas:pago_confirmar', pago_id=pago.id)

        pago.banco = banco
        pago.numero_boleta = numero_boleta
        try:
            from datetime import datetime
            pago.fecha_pago = datetime.strptime(fecha_pago, "%Y-%m-%d").date()
        except Exception:
            messages.error(request, "Fecha de pago inválida (usa formato AAAA-MM-DD).")
            return redirect('citas:pago_confirmar', pago_id=pago.id)
        pago.notas = notas
        pago.comprobante = comprobante
        pago.estado = 'pendiente_verificacion'
        pago.save()

        messages.success(request, "¡Gracias! Tu comprobante fue enviado. Verificaremos en breve.")
        return redirect('citas:pago_detalle', pago_id=pago.id)

    return render(request, "citas/confirmar_pago.html", {"pago": pago})


# ========= NUEVO: Mis Citas (cliente) =========
@login_required
def mis_citas(request):
    """
    Listado HTML de las citas del cliente autenticado, con mismos filtros de PDF.
    Template: citas/mis_citas.html
    """
    base_qs = Cita.objects.filter(usuario=request.user)
    citas_qs, filtros = _filtrar_citas_base(request, base_qs)

    context = {
        "citas": citas_qs,
        "filtros": filtros,
        "estados_choices": dict(Cita.ESTADOS),
        "servicios": Servicio.objects.all().order_by("nombre"),
        "ahora": timezone.localtime(timezone.now()),
    }
    return render(request, "citas/mis_citas.html", context)
