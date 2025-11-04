from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistroForm

def registro(request):
    if request.method == 'POST':
        print("FORMULARIO RECIBIDO VIA POST")  
        form = RegistroForm(request.POST)
        print("FORMULARIO CREADO")             
        
        if form.is_valid():
            print("FORMULARIO VALIDO")                  
            user = form.save()
            print(f"USUARIO CREADO: {user.username}")   
            
            # CORRECCIÓN: Enviar correo de forma asíncrona y manejar mejor los errores
            try:
                # Preparar el contenido del correo
                nombre_completo = user.get_full_name() or user.username
                
                send_mail(
                    '¡Bienvenido/a a MyVetPet - Registro Exitoso!',
                    f'''
                    Hola {nombre_completo},
                    
                    ¡Nos alegra darte la bienvenida a MyVetPet!

                    Tu registro se completó correctamente. 
                    A partir de ahora podrás:
                    - Registrar y gestionar tus mascotas
                    - Programar citas veterinarias
                    - Acceder a tu historial médico
                    - Conocer todos nuestros servicios
                    
                    Gracias por confiar en nosotros para el cuidado
                    de tus mascotas.
                    
                    Atentamente,  
                    El equipo de MyVetPet
                    ''',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                print(f"CORREO ENVIADO EXITOSAMENTE A: {user.email}")  
                
            except Exception as e:
                # Manejo de errores en el envío de correo
                print(f"ERROR ENVIANDO CORREO: {e}")
                # No interrumpe el registro, solo informa del error
                messages.warning(request, 'Tu cuenta se creó correctamente, pero hubo un problema al enviar el correo de confirmación.')
            
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.get_full_name()}! Tu cuenta ha sido creada exitosamente.')  
            return redirect('home')
        else:
            print("FORMULARIO INVALIDO")       
            print("Errores:", form.errors)     
            messages.error(request, 'Por favor corrige los errores en el formulario.')  
    else:
        form = RegistroForm()                  
        print("MOSTRANDO FORMULARIO VACIO")    
    
    return render(request, 'usuarios/registro.html', {'form': form})