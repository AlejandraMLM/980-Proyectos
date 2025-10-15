from django.shortcuts import render, redirect, get_object_or_404    # Funciones para renderizar, redireccionar y obtener objetos
from django.contrib.auth.decorators import login_required           # Decorador para requerir autenticacion
from django.contrib import messages                                 # Sistema de mensajes de Django
from servicios.models import Servicio                               # Modelos de servicios y citas
from citas.models import Cita                       
from usuarios.models import Usuario                                 # Modelo de usuarios personalizado
from .forms import ServicioForm                                     # Formulario para servicios


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:  # Verifica si el usuario esta autenticado y es staff
            return view_func(request, *args, **kwargs)               # Ejecuta la vista si es administrador
        else:
            messages.error(request, "No tienes permisos de administrador")  # Mensaje de error
            return redirect('login')  # Redirige al login si no es administrador
    return wrapper

@login_required  # Requiere que el usuario este logueado
@admin_required  # Requiere que el usuario sea administrador
def panel_principal(request):
    """Panel principal con datos reales de la base de datos"""
    try:
        # Obtener datos de la base de datos
        total_servicios = Servicio.objects.count()                          # Cuenta total de servicios
        total_citas = Cita.objects.count()                                  # Cuenta total de citas
        total_usuarios = Usuario.objects.count()                            # Cuenta total de usuarios
        citas_pendientes = Cita.objects.filter(estado='pendiente').count()  # Cuenta citas pendientes
        
        context = {  # Contexto con datos reales
            'total_servicios': total_servicios,
            'total_citas': total_citas,
            'total_usuarios': total_usuarios,
            'citas_pendientes': citas_pendientes,
        }
        return render(request, 'administrador/panel.html', context)  # Renderiza el panel con datos
        
    except Exception as e:  
        messages.error(request, f"Error al cargar el panel de administracion: {str(e)}")  # Mensaje de error
        return redirect('home')  # Redirige al home en caso de error

@login_required  
@admin_required  
def gestion_servicios(request):
    """Gestion de servicios"""
    try:
        servicios = Servicio.objects.all().order_by('-id')  # Obtiene todos los servicios ordenados por ID descendente
        return render(request, 'administrador/gestion_servicios.html', {'servicios': servicios})  # Renderiza la gestion de servicios
        
    except Exception as e:  # Captura errores al cargar servicios
        messages.error(request, f"Error al cargar los servicios: {str(e)}")  # Mensaje de error
        return render(request, 'administrador/gestion_servicios.html', {'servicios': []})  # Renderiza con lista vacia

@login_required  
@admin_required  
def agregar_servicio(request):
    """Agregar nuevo servicio"""
    if request.method == 'POST':  # Si el formulario fue enviado
        form = ServicioForm(request.POST, request.FILES)  # Crea formulario con datos y archivos
        if form.is_valid():  # Valida el formulario
            servicio = form.save()  # Guarda el servicio en la base de datos
            messages.success(request, f'Servicio "{servicio.nombre}" agregado exitosamente')  # Mensaje de exito
            return redirect('administrador:gestion_servicios')  # Redirige a la gestion de servicios
        else:
            messages.error(request, 'Error en el formulario. Por favor corrige los errores.')  # Mensaje de error
    else:
        form = ServicioForm()  
    
    return render(request, 'administrador/agregar_servicio.html', {'form': form})  # Renderiza el formulario

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
        
        return render(request, 'administrador/editar_servicio.html', {
            'form': form, 
            'servicio': servicio
        })
        
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