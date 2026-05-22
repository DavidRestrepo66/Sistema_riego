"""
Simula las lecturas del Arduino sin necesidad de conectarlo.
Genera datos realistas y los guarda en MongoDB y SQL Server,
ejecutando el mismo pipeline que guardar_datos.py.
"""

import sys
import random
import time
from datetime import datetime

sys.path.insert(0, 'SensoresWeb_MongoDB')

from services.sensor_service import SensorService
from utils.sql_server import get_sql_server_connection

ID_DISPOSITIVO = 1
ID_ZONA = 1
NUMERO_LECTURAS = 5
PAUSA_SEGUNDOS = 1  # 0 para insertar todo sin esperar


def generar_linea_csv():
    """Genera una línea CSV en el mismo formato que envía el Arduino."""
    temp_dht = round(random.uniform(18.0, 35.0), 1)
    humedad  = round(random.uniform(30.0, 80.0), 1)
    temp_bmp = round(temp_dht + random.uniform(-0.5, 0.5), 1)
    presion  = round(random.uniform(1005.0, 1025.0), 1)
    luz      = round(random.uniform(100.0, 1000.0), 1)
    return f"{temp_dht},{humedad},{temp_bmp},{presion},{luz}"


def procesar_linea(linea):
    """Misma lógica de parseo que en guardar_datos.py."""
    datos = linea.split(",")
    if len(datos) != 5:
        raise ValueError(f"Formato incorrecto: {linea}")
    return {
        "fecha":    datetime.now(),
        "temp_dht": float(datos[0]),
        "humedad":  float(datos[1]),
        "temp_bmp": float(datos[2]),
        "presion":  float(datos[3]),
        "luz":      float(datos[4]),
    }


def guardar_en_mongo(lectura):
    SensorService.guardar_lectura(lectura)
    print("  [MongoDB]    OK")


def guardar_en_sql(lectura):
    conn = get_sql_server_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO lecturas
            (id_dispositivo, id_zona, fecha,
             temp_dht, humedad, temp_bmp, presion, luz)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ID_DISPOSITIVO,
            ID_ZONA,
            lectura["fecha"],
            lectura["temp_dht"],
            lectura["humedad"],
            lectura["temp_bmp"],
            lectura["presion"],
            lectura["luz"],
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()
    print("  [SQL Server] OK")


def main():
    print(f"Simulando {NUMERO_LECTURAS} lecturas de Arduino...\n")

    ok = 0
    for i in range(1, NUMERO_LECTURAS + 1):
        linea = generar_linea_csv()
        print(f"Lectura {i}/{NUMERO_LECTURAS}: {linea}")

        try:
            lectura = procesar_linea(linea)

            try:
                guardar_en_mongo(lectura)
            except Exception as e:
                print(f"  [MongoDB]    ERROR: {e}")

            try:
                guardar_en_sql(lectura)
            except Exception as e:
                print(f"  [SQL Server] ERROR: {e}")

            ok += 1
        except Exception as e:
            print(f"  ERROR al parsear: {e}")

        if PAUSA_SEGUNDOS and i < NUMERO_LECTURAS:
            time.sleep(PAUSA_SEGUNDOS)

    print(f"\nResumen: {ok}/{NUMERO_LECTURAS} lecturas procesadas correctamente.")


if __name__ == "__main__":
    main()
