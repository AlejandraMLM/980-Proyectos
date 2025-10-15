from django.shortcuts import render, redirect   # Funciones para renderizar templates y redireccionar
from django.contrib.auth import login           # Funcion para iniciar sesion automaticamente
from django.contrib import messages             # Sistema de mensajes de Django
from .forms import RegistroForm                 # Formulario personalizado de registro

def registro(request):
    # Verifica si la peticion es POST (envio de formulario)
    if request.method == 'POST':
        print("FORMULARIO RECIBIDO VIA POST")  
        form = RegistroForm(request.POST)      # Crea formulario con datos enviados
        print("FORMULARIO CREADO")             
        
        # Valida si el formulario es correcto
        if form.is_valid():
            print("FORMULARIO VALIDO")                  
            user = form.save()                 # Guarda el usuario en la base de datos
            print(f"USUARIO CREADO: {user.username}")   
            login(request, user)               # Inicia sesion automaticamente al usuario
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada.')  
            return redirect('home')            # Redirige a la pagina de inicio
        else:
            print("FORMULARIO INVALIDO")       
            print("Errores:", form.errors)     
            messages.error(request, 'Por favor corrige los errores en el formulario.')  
    else:
        form = RegistroForm()                  
        print("MOSTRANDO FORMULARIO VACIO")    
    
    # Renderiza la plantilla de registro con el formulario
    return render(request, 'usuarios/registro.html', {'form': form})