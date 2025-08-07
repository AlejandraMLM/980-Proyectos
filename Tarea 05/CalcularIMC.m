#Definición de las categorías
bajoPeso = "Bajo peso";
pesoNormal = "Peso normal";
sobrePeso = "Sobrepeso";

#Bucle principal
while true
    disp("------------------------------");
    fprintf("\n");

    #Mostrar opciones
    disp("Opciones");
    disp("1. Calcular IMC y mostrar resultados");
    disp("2. Leer información del archivo");
    disp("3. Borrar información del archivo");
    disp("4. Salir del programa");

    #Leer opción del usuario
    opcion = input("Ingrese la opción deseada: ");

    #Validar la opción
    if not (1<= opcion <=4)
        disp("Opción no válida. Intente de nuevo.");
        continue;
    end

    #Ejecutar la acción según la opción
    switch opcion
        case 1
            #Calcular IMC y mostrar resultados
            nombre = input("Ingrese su nombre: ", "s");
            peso = input("Ingrese su peso en kilogramos: ");
            altura = input("Ingrese su altura en metros: ");

            imc = peso / (altura^2);

            #Clasificar el IMC
            if imc < 18.5
                categoria = bajoPeso;
            elseif imc < 25
                categoria = pesoNormal;
            else
                categoria = sobrePeso;
            end

            #Mostrar resultados
            fprintf("\nNombre: %s\n", nombre);
            fprintf("IMC: %.2f\n", imc);
            fprintf("Categoría: %s\n", categoria);

            #Guardar en archivo
            archivo = fopen("imc.txt", "a");
            fprintf(archivo, "Nombre: %s\nIMC: %.2f\nCategoría: %s\n\n", nombre, imc, categoria);
            fclose(archivo);

        case 2
            #Leer información del archivo
            if exist("imc.txt", "file")
                disp("Contenido de imc.txt:");
                tipo = fopen("imc.txt", "r");
                while ~feof(tipo)
                    linea = fgetl(tipo);
                    disp(linea);
                end
                fclose(tipo);
            else
                disp("No existe el archivo imc.txt.");
            end

        case 3
            #Borrar información del archivo
            if exist("imc.txt", "file")
                delete("imc.txt");
                disp("Archivo imc.txt eliminado.");
            else
                disp("No existe el archivo imc.txt.");
            end

        case 4
            #Salir del programa
            disp("¡Gracias por usar el programa!");
            break;
    end
end
