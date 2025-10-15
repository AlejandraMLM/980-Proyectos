from django.shortcuts import render, redirect, get_object_or_404    # Funciones para renderizar, redireccionar y obtener objetos
from django.contrib.auth.decorators import login_required           # Decorador para requerir autenticacion
from django.contrib import messages                                 # Sistema de mensajes de Django
from django.http import JsonResponse                                # Para respuestas JSON (carrito dinamico)
from .models import Carrito, Cita                                   # Importa los modelos Carrito y Cita
from servicios.models import Servicio                               # Importa el modelo Servicio
from .forms import CitaForm                                         # Importa el formulario de Cita

@login_required  # Requiere que el usuario este logueado
def agregar_al_carrito(request, servicio_id):
    """Agrega un servicio al carrito del usuario"""
    try:
        servicio = get_object_or_404(Servicio, id=servicio_id)  # Obtiene el servicio o devuelve 404
        
        # Verifica si el servicio esta disponible
        if not servicio.disponible:
            messages.error(request, "Este servicio no esta disponible actualmente")     # Mensaje de error
            return redirect('home')                                                     # Redirige al home
            
        # Crea o obtiene el item del carrito
        carrito_item, created = Carrito.objects.get_or_create(
            usuario=request.user,       # Usuario actual
            servicio=servicio,          # Servicio seleccionado
            defaults={'cantidad': 1}    # Valor por defecto si se crea nuevo
        )
        
        if not created:
            # Si ya existe, aumenta la cantidad
            carrito_item.cantidad += 1  # Incrementa la cantidad
            carrito_item.save()         # Guarda los cambios
            
        messages.success(request, f'"{servicio.nombre}" agregado al carrito')   # Mensaje de exito
        return redirect('home')                                                 # Redirige al home
        
    except Exception as e:
        messages.error(request, f"Error al agregar al carrito: {str(e)}")       # Mensaje de error
        return redirect('home')                                                 # Redirige al home

@login_required  
def ver_carrito(request):
    """Muestra el carrito de compras del usuario"""
    try:
        carrito_items = Carrito.objects.filter(usuario=request.user)                 # Obtiene items del carrito del usuario
        total = sum(item.servicio.precio * item.cantidad for item in carrito_items)  # Calcula el total
        
        context = {
            'carrito_items': carrito_items,     # Items del carrito
            'total': total,                     # Total a pagar
        }
        return render(request, 'citas/carrito.html', context)  # Renderiza el template del carrito
        
    except Exception as e:
        messages.error(request, f"Error al cargar el carrito: {str(e)}")                 # Mensaje de error
        return render(request, 'citas/carrito.html', {'carrito_items': [], 'total': 0})  # Renderiza carrito vacio

@login_required  
def eliminar_del_carrito(request, item_id):
    """Elimina un item del carrito"""
    try:
        carrito_item = get_object_or_404(Carrito, id=item_id, usuario=request.user)     # Obtiene el item del carrito
        servicio_nombre = carrito_item.servicio.nombre                                  # Guarda el nombre para el mensaje
        carrito_item.delete()                                                           # Elimina el item del carrito
        messages.success(request, f'"{servicio_nombre}" eliminado del carrito')         # Mensaje de exito
        return redirect('citas:ver_carrito')                                            # Redirige al carrito
        
    except Exception as e:
        messages.error(request, f"Error al eliminar del carrito: {str(e)}")             # Mensaje de error
        return redirect('citas:ver_carrito')                                            # Redirige al carrito

@login_required  
def actualizar_cantidad(request, item_id):
    """Actualiza la cantidad de un item en el carrito (para AJAX)"""
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try:
            carrito_item = get_object_or_404(Carrito, id=item_id, usuario=request.user) # Obtiene el item del carrito
            nueva_cantidad = int(request.POST.get('cantidad', 1))                       # Obtiene la nueva cantidad
            
            if nueva_cantidad > 0:
                carrito_item.cantidad = nueva_cantidad                                  # Actualiza la cantidad
                carrito_item.save()                                                     # Guarda los cambios
                
                # Recalcula totales
                carrito_items = Carrito.objects.filter(usuario=request.user)                    # Obtiene todos los items
                total = sum(item.servicio.precio * item.cantidad for item in carrito_items)     # Calcula nuevo total
                
                return JsonResponse({
                    'success': True,
                    'subtotal': carrito_item.servicio.precio * carrito_item.cantidad,           # Subtotal del item
                    'total': total  # Total del carrito
                })
            else:
                return JsonResponse({'success': False, 'error': 'Cantidad invalida'})           # Respuesta de error
                
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})                            # Respuesta de error
    
    return JsonResponse({'success': False, 'error': 'Metodo no permitido'})                     # Respuesta de error

@login_required  
def agendar_cita(request):
    """Procesa el agendamiento de cita desde el carrito"""
    # Obtiene items del carrito para mostrar en el template
    carrito_items = Carrito.objects.filter(usuario=request.user)
    
    # Verifica que haya items en el carrito
    if not carrito_items:
        messages.error(request, 'No hay servicios en el carrito para agendar.')
        return redirect('citas:ver_carrito')
    
    if request.method == 'POST':
        form = CitaForm(request.POST)
        if form.is_valid():
            try:
                # Para cada servicio en el carrito, crear una cita
                for item in carrito_items:
                    cita = form.save(commit=False)
                    cita.usuario = request.user
                    cita.servicio = item.servicio  # Asigna el servicio del carrito
                    cita.estado = 'pendiente'      # Estado inicial
                    cita.save()
                
                # Limpia el carrito después de agendar
                carrito_items.delete()
                
                messages.success(request, '¡Citas agendadas exitosamente! Recibirás un correo de confirmación.')
                return redirect('home')
                
            except Exception as e:
                messages.error(request, f'Error al agendar las citas: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = CitaForm()
    
    total = sum(item.servicio.precio * item.cantidad for item in carrito_items)
    
    context = {
        'form': form,
        'carrito_items': carrito_items,
        'total': total,
    }
    return render(request, 'citas/agendar_cita.html', context)