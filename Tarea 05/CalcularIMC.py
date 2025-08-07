# Definición de las categorías
bajo_peso = "Bajo peso"
peso_normal = "Peso normal"
sobre_peso = "Sobrepeso"

# Bucle principal
while True:
    print("------------------------------\n")

    # Mostrar opciones
    print("Opciones")
    print("1. Calcular IMC y mostrar resultados")
    print("2. Leer información del archivo")
    print("3. Borrar información del archivo")
    print("4. Salir del programa")

    # Leer opción del usuario
    opcion = int(input("Ingrese la opción deseada: "))

    # Validar opción
    if opcion < 1 or opcion > 4:
        print("Opción no válida. Intente de nuevo.\n")
        continue

    # Ejecutar la acción según la opción
    if opcion == 1:
        # Calcular IMC y mostrar resultados
        nombre = input("Ingrese su nombre: ")
        peso = float(input("Ingrese su peso en kilogramos: "))
        altura = float(input("Ingrese su altura en metros: "))

        # Cálculo del IMC
        imc = peso / (altura * altura)

        # Clasificar el IMC
        if imc < 18.5:
            categoria = bajo_peso
        elif imc < 25:
            categoria = peso_normal
        else:
            categoria = sobre_peso

        # Mostrar resultados
        print("\nNombre:", nombre)
        print("IMC:", round(imc, 2))
        print("Categoría:", categoria)

        # Guardar en archivo
        archivo = open("imc.txt", "a")
        archivo.write("Nombre: " + nombre + "\n")
        archivo.write("IMC: " + str(round(imc, 2)) + "\n")
        archivo.write("Categoría: " + categoria + "\n\n")
        archivo.close()

    elif opcion == 2:
        # Leer información del archivo
        archivo = open("imc.txt", "r")
        contenido = archivo.read()
        print("\nContenido de imc.txt:")
        print(contenido)
        archivo.close()

    elif opcion == 3:
        # Borrar información del archivo
        import os
        os.remove("imc.txt")
        print("Archivo imc.txt eliminado.")

    elif opcion == 4:
        # Salir del programa
        print("¡Gracias por usar el programa!")
        break
