import psycopg2
import re

#CONEXIÓN A BASE DE DATOS

def conectar_bd():
    try:
        conn = psycopg2.connect(
            "dbname=gasolinera user=postgres password=koala host=localhost port=5432"
        )
        return conn
    except Exception as e:
        print("Error al conectar con la base de datos:", e)
        return None

# CREAR TABLA EN BASE DE DATOS

def inicializar_bd():
    """Crea la tabla en la base de datos si no existe"""
    try:
        conn = conectar_bd()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS facturas_gasolina (
                        cliente TEXT NOT NULL,
                        placa TEXT NOT NULL,
                        combustible TEXT NOT NULL,
                        litros REAL NOT NULL,
                        total REAL NOT NULL
                    )
                """)
                conn.commit()
            conn.close()
    except Exception as e:
        print("Error inicializando base de datos:", e)



# VALIDACIONES DE FORMATO

def pedir_nombre_apellido(mensaje):
    patron = r"^[A-Za-z]+(?: [A-Za-z]+)+$"
    while True:
        nombre = input(mensaje).strip()
        if re.match(patron, nombre):
            return nombre
        else:
            print("Ingrese nombre y apellido(s) separados por espacio. Solo letras sin signos ni números.")


def pedir_placa(mensaje):
    patron = r"^P[0-9]{3}[A-Z]{3}$"
    while True:
        placa = input(mensaje).strip().upper()
        if re.match(patron, placa):
            return placa
        else:
            print("La placa debe tener formato P123ABC.")


def pedir_entero(mensaje, minimo=1, maximo=None):
    while True:
        try:
            valor = int(input(mensaje))
            if valor < minimo:
                print(f"El valor debe ser mayor o igual a {minimo}")
            elif maximo and valor > maximo:
                print(f"El valor debe ser menor o igual a {maximo}")
            else:
                return valor
        except ValueError:
            print("Debe ingresar un número entero válido.")


def pedir_flotante(mensaje, minimo=0.1):
    while True:
        try:
            valor = float(input(mensaje))
            if valor < minimo:
                print(f"El valor debe ser mayor a {minimo}")
            else:
                return valor
        except ValueError:
            print("Debe ingresar un número válido.")



# LÓGICA DEL PROGRAMA

precios_combustible = {
    1: ("Gasolina Regular", 7.84),
    2: ("Gasolina Premium", 8.23),
    3: ("Diesel", 7.39)
}


def calcular_total(tipo, litros):
    nombre, precio = precios_combustible[tipo]
    return nombre, litros * precio


def guardar_factura(cliente, placa, combustible, litros, total):
    try:
        # Guardar en archivo
        with open("salida.txt", "a", encoding="utf-8") as f:
            f.write(f"{cliente},{placa},{combustible},{litros},{total:.2f}\n")

        # Guardar en BD
        conn = conectar_bd()
        if conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO facturas_gasolina (cliente, placa, combustible, litros, total) VALUES (%s,%s,%s,%s,%s)",
                    (cliente, placa, combustible, litros, total)
                )
                conn.commit()
            conn.close()
        print("Factura guardada correctamente.")
    except Exception as e:
        print("Error al guardar factura:", e)


def mostrar_historial():
    print("\n--- Historial desde archivo ---")
    try:
        with open("salida.txt", "r", encoding="utf-8") as f:
            for linea in f:
                print(" -", linea.strip())
    except FileNotFoundError:
        print("No hay facturas registradas en archivo.")

    print("\n--- Historial desde base de datos ---")
    try:
        conn = conectar_bd()
        if conn:
            with conn.cursor() as cur:
                cur.execute("SELECT cliente, placa, combustible, litros, total FROM facturas_gasolina")
                registros = cur.fetchall()
                if registros:
                    for r in registros:
                        print(f"Cliente={r[0]}, Placa={r[1]}, Combustible={r[2]}, Litros={r[3]}, Total=Q{r[4]:.2f}")
                else:
                    print("No hay facturas en la base de datos.")
            conn.close()
    except Exception as e:
        print("Error mostrando historial:", e)


def borrar_historial():
    print("\n--- BORRAR HISTORIAL ---")
    print("1. Borrar una factura específica")
    print("2. Borrar todas las facturas")
    print("3. Borrar todas las facturas de una placa")
    print("4. Cancelar")

    opcion = pedir_entero("Seleccione una opción: ", 1, 4)

    if opcion == 1:
        placa = input("Ingrese la placa del vehículo de la factura a borrar: ").strip().upper()

        # Borrar en archivo
        try:
            nuevas_lineas = []
            with open("salida.txt", "r", encoding="utf-8") as f:
                for linea in f:
                    if not (placa in linea):
                        nuevas_lineas.append(linea)
            with open("salida.txt", "w", encoding="utf-8") as f:
                f.writelines(nuevas_lineas)
            print("Factura borrada del archivo (si existía).")
        except FileNotFoundError:
            print("No hay archivo de facturas.")

        # Borrar en BD
        try:
            conn = conectar_bd()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM facturas_gasolina WHERE placa=%s", (placa,))
                    conn.commit()
                conn.close()
                print("Factura borrada de la base de datos (si existía).")
        except Exception as e:
            print("Error borrando factura en base de datos:", e)

    elif opcion == 2:
        # BORRAR TODO
        try:
            with open("salida.txt", "w", encoding="utf-8"):
                pass
            print("Archivo borrado correctamente.")
        except Exception as e:
            print("Error borrando archivo:", e)

        try:
            conn = conectar_bd()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM facturas_gasolina")
                    conn.commit()
                conn.close()
                print("Historial en base de datos borrado.")
        except Exception as e:
            print("Error borrando historial en base de datos:", e)

    elif opcion == 3:
        placa = input("Ingrese la placa de las facturas a borrar: ").strip().upper()

        # Borrar en archivo
        try:
            nuevas_lineas = []
            with open("salida.txt", "r", encoding="utf-8") as f:
                for linea in f:
                    if placa not in linea:
                        nuevas_lineas.append(linea)
            with open("salida.txt", "w", encoding="utf-8") as f:
                f.writelines(nuevas_lineas)
            print(f"Facturas con placa {placa} borradas del archivo (si existían).")
        except FileNotFoundError:
            print("No hay archivo de facturas.")

        # Borrar en BD
        try:
            conn = conectar_bd()
            if conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM facturas_gasolina WHERE placa=%s", (placa,))
                    conn.commit()
                conn.close()
                print(f"Facturas con placa {placa} borradas de la base de datos (si existían).")
        except Exception as e:
            print("Error borrando facturas en base de datos:", e)

    elif opcion == 4:
        print("Cancelando borrado. Regresando al menú principal...")



# FUNCIÓN PRINCIPAL

def menu():
    inicializar_bd()
    while True:
        print("\n========== MENÚ PRINCIPAL ==========")
        print("1. Registrar factura")
        print("2. Ver historial")
        print("3. Borrar historial")
        print("4. Salir")

        opcion = pedir_entero("Seleccione una opción (1-4): ", 1, 4)

        if opcion == 1:
            cliente = pedir_nombre_apellido("Nombre y apellido del cliente: ")
            placa = pedir_placa("Placa del vehículo (P123ABC): ")

            print("\n-----Tipos de combustible-----")
            for k, v in precios_combustible.items():
                print(f"{k}. {v[0]} - Q{v[1]:.2f} por litro")

            tipo = pedir_entero("Seleccione el tipo (1-3): ", 1, 3)
            litros = pedir_flotante("Litros a despachar: ", 0.1)

            combustible, total = calcular_total(tipo, litros)

            print("\n--- FACTURA ---")
            print(f"Cliente: {cliente}")
            print(f"Vehículo: {placa}")
            print(f"Combustible: {combustible}")
            print(f"Litros: {litros:.2f}")
            print(f"Total a pagar: Q{total:.2f}")
            print("---------------------")

            guardar_factura(cliente, placa, combustible, litros, total)

        elif opcion == 2:
            mostrar_historial()

        elif opcion == 3:
            borrar_historial()

        elif opcion == 4:
            print("Gracias por usar el sistema. Saliendo...")
            break

# EJECUCIÓN

menu()
