# Programa de Cobro y Facturación de Parqueo
import psycopg2
from datetime import datetime, timedelta
import math
import re

# Conexión a la base de datos
def conectar_bd():
    try:
        conn = psycopg2.connect("dbname=parqueo user=postgres password=koala host=localhost port=5432")
        return conn
    except Exception as e:
        print("Error al conectar con la base de datos:", e)
        return None

# Manejo de errores
def pedir_entero(mensaje, minimo=0):
    while True:
        try:
            valor = int(input(mensaje))
            if valor < minimo:
                print(f"El valor debe ser mayor o igual a {minimo}")
            else:
                return valor
        except ValueError:
            print("Solo se permiten números enteros.")

def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor == "":
            print("Este campo no puede estar vacío.")
        else:
            return valor

# =========================
# VALIDACIONES
# =========================
def pedir_nombre_completo(mensaje):
    patron = r"^[A-Za-z]+ [A-Za-z]+$"
    while True:
        nombre = input(mensaje).strip()
        if re.match(patron, nombre):
            return nombre
        else:
            print("Ingrese nombre y apellido separados por un solo espacio. Solo se permiten letras sin signos ni números.")

def pedir_nit(mensaje):
    while True:
        nit = input(mensaje).strip()
        if nit.isdigit() and len(nit) == 9:
            return nit
        else:
            print("El NIT debe contener exactamente 9 dígitos numéricos.")

def pedir_placa(mensaje):
    patron = r"^P[0-9]{3}[A-Z]{3}$"
    while True:
        placa = input(mensaje).strip().upper()
        if re.match(patron, placa):
            return placa
        else:
            print("La placa debe tener el formato P123ABC (7 caracteres, solo letras y números).")

def pedir_hora(mensaje):
    while True:
        try:
            hora_str = input(mensaje).strip()
            hora = datetime.strptime(hora_str, "%H:%M")
            return hora
        except ValueError:
            print("Formato inválido. Use HH:MM (ejemplo: 14:30)")

# Lógica del programa
def calcular_monto(horas):
    if horas <= 1:
        return 15
    else:
        return 15 + (horas - 1) * 20

def inicializar_bd():
    try:
        conn = conectar_bd()
        if conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS facturas (                    
                    nombre TEXT NOT NULL,
                    nit BIGINT NOT NULL,
                    placa TEXT NOT NULL,
                    horas INT NOT NULL,
                    monto INT NOT NULL,
                    tiempo TEXT NOT NULL
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        print("Error inicializando base de datos:", e)

def guardar_factura(nombre, nit, placa, horas, monto, tiempo):
    try:
        with open("facturas.txt", "a", encoding="utf-8") as f:
            f.write(f"{nombre},{nit},{placa},{horas},{monto},{tiempo}\n")

        conn = conectar_bd()
        if conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO facturas (nombre, nit, placa, horas, monto, tiempo) VALUES (%s, %s, %s, %s, %s, %s)",
                (nombre, nit, placa, horas, monto, tiempo)
            )
            conn.commit()
            cur.close()
            conn.close()
    except Exception as e:
        print("Error al guardar factura:", e)

def mostrar_historial():
    print("\n Historial desde archivo:")
    try:
        with open("facturas.txt", "r", encoding="utf-8") as f:
            for linea in f:
                print(" -", linea.strip())
    except FileNotFoundError:
        print("Aún no hay facturas en archivo.")

    print("\n Historial desde base de datos:")
    try:
        conn = conectar_bd()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT nombre, nit, placa, horas, monto, tiempo FROM facturas")
            registros = cur.fetchall()
            for r in registros:
                print(f" - Cliente: {r[0]}, NIT: {r[1]}, Placa: {r[2]}, Tiempo: {r[5]}, Horas facturadas: {r[3]}, Monto: Q{r[4]}")
            cur.close()
            conn.close()
    except Exception as e:
        print("Error al mostrar historial en base de datos:", e)

def borrar_historial():
    try:
        open("facturas.txt", "w").close()
        print("Archivo de facturas borrado.")
    except Exception as e:
        print("Error borrando archivo:", e)

    try:
        conn = conectar_bd()
        if conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM facturas")
            conn.commit()
            cur.close()
            conn.close()
            print("Historial de base de datos borrado.")
    except Exception as e:
        print("Error borrando historial en base de datos:", e)

# MENU PRINCIPAL
def menu():
    inicializar_bd()
    while True:
        print("\n===== SISTEMA DE PARQUEO =====")
        print("1. Registrar factura")
        print("2. Mostrar historial")
        print("3. Borrar historial")
        print("4. Salir")

        opcion = pedir_entero("Seleccione una opción: ", minimo=1)

        if opcion == 1:
            # Ingresar datos del cliente
            nombre = pedir_nombre_completo("Ingrese nombre y apellido del cliente (solo letras, un espacio): ")
            nit = pedir_nit("Ingrese NIT del cliente (9 dígitos): ")
            placa = pedir_placa("Ingrese número de placa (P123ABC): ")

            # Ingresar horas con reintento sin perder datos
            while True:
                hora_entrada = pedir_hora("Ingrese hora de entrada (HH:MM): ")
                hora_salida = pedir_hora("Ingrese hora de salida (HH:MM): ")

                if hora_salida <= hora_entrada:
                    print("Error: La hora de salida debe ser posterior a la hora de entrada. Intente de nuevo.")
                else:
                    break

            # Calcular diferencia de tiempo
            diferencia = hora_salida - hora_entrada
            total_minutos = diferencia.total_seconds() / 60
            horas_exactas = total_minutos / 60

            # Redondear hacia arriba
            horas_facturadas = math.ceil(horas_exactas)

            monto = calcular_monto(horas_facturadas)
            tiempo_texto = str(diferencia)

            print(f"\n Factura generada: Cliente={nombre}, NIT={nit}, Placa={placa}, Tiempo={tiempo_texto}, Horas facturadas={horas_facturadas}, Monto=Q{monto}")
            guardar_factura(nombre, nit, placa, horas_facturadas, monto, tiempo_texto)

        elif opcion == 2:
            mostrar_historial()

        elif opcion == 3:
            borrar_historial()

        elif opcion == 4:
            print("Saliendo del sistema. ¡Gracias!")
            break

        else:
            print("Opción no válida.")

# Ejecutar programa
menu()