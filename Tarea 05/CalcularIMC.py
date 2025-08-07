import psycopg2

# Conexión a PostgreSQL
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="koala",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

# Definición de categorías
bajo_peso = "Bajo peso"
peso_normal = "Peso normal"
sobre_peso = "Sobrepeso"

def guardar_en_archivo(nombre, imc, categoria):
    with open("imc.txt", "a") as f:
        f.write(f"Nombre: {nombre}\nIMC: {imc:.2f}\nCategoría: {categoria}\n\n")

def leer_archivo():
    try:
        with open("imc.txt", "r") as f:
            print("Contenido de imc.txt:")
            for linea in f:
                print(linea.strip())
    except FileNotFoundError:
        print("No existe el archivo imc.txt.")

def borrar_archivo():
    import os
    if os.path.exists("imc.txt"):
        os.remove("imc.txt")
        print("Archivo imc.txt eliminado.")
    else:
        print("No existe el archivo imc.txt.")

def borrar_base_datos():
    cursor.execute("DELETE FROM imc")
    conn.commit()
    print("Registros de la base de datos eliminados.")

while True:
    print("------------------------------\n")
    print("Opciones")
    print("1. Calcular IMC y mostrar resultados")
    print("2. Leer información del archivo")
    print("3. Borrar información del archivo y base de datos")
    print("4. Salir del programa")

    opcion_str = input("Ingrese la opción deseada: ")
    if not opcion_str.isdigit() or int(opcion_str) not in range(1,5):
        print("Opción no válida. Intente de nuevo.")
        continue

    opcion = int(opcion_str)

    if opcion == 1:
        nombre = input("Ingrese su nombre: ")
        peso = float(input("Ingrese su peso en kilogramos: "))
        altura = float(input("Ingrese su altura en metros: "))
        imc = peso / (altura ** 2)

        if imc < 18.5:
            categoria = bajo_peso
        elif imc < 25:
            categoria = peso_normal
        else:
            categoria = sobre_peso

        print(f"\nNombre: {nombre}")
        print(f"IMC: {imc:.2f}")
        print(f"Categoría: {categoria}")

        guardar_en_archivo(nombre, imc, categoria)

        cursor.execute(
            "INSERT INTO imc (nombre, imc, categoria) VALUES (%s, %s, %s)",
            (nombre, imc, categoria)
        )
        conn.commit()

    elif opcion == 2:
        leer_archivo()

    elif opcion == 3:
        borrar_archivo()
        borrar_base_datos()

    elif opcion == 4:
        print("¡Gracias por usar el programa!")
        break

cursor.close()
conn.close()
