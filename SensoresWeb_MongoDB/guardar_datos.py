import serial

from datetime import datetime

from config import Config

from services.sensor_service import (
    SensorService
)

from utils.sql_server import (
    get_sql_server_connection
)

arduino = serial.Serial(

    Config.ARDUINO_PORT,

    Config.BAUD_RATE
)

print(
    "Esperando datos del Arduino..."
)

while True:

    try:

        linea = arduino.readline() \
            .decode() \
            .strip()

        print(
            "Dato recibido:",
            linea
        )

        datos = linea.split(",")

        if len(datos) == 5:

            lectura = {

                "fecha": datetime.now(),

                "temp_dht": float(datos[0]),

                "humedad": float(datos[1]),

                "temp_bmp": float(datos[2]),

                "presion": float(datos[3]),

                "luz": float(datos[4])
            }

            # GUARDAR EN MONGODB

            SensorService.guardar_lectura(
                lectura
            )

            print(
                "Guardado en MongoDB Atlas"
            )

            # GUARDAR EN SQL SERVER

            try:

                sql_conn = get_sql_server_connection()

                cursor = sql_conn.cursor()

                cursor.execute(

                    """
                    INSERT INTO lecturas
                    (
                        fecha,
                        temp_dht,
                        humedad,
                        temp_bmp,
                        presion,
                        luz
                    )

                    VALUES (?, ?, ?, ?, ?, ?)
                    """,

                    (
                        lectura["fecha"],
                        lectura["temp_dht"],
                        lectura["humedad"],
                        lectura["temp_bmp"],
                        lectura["presion"],
                        lectura["luz"]
                    )

                )

                sql_conn.commit()

                cursor.close()

                sql_conn.close()

                print(
                    "Guardado en SQL Server"
                )

            except Exception as sql_error:

                print(
                    "Error SQL Server:",
                    sql_error
                )

    except Exception as e:

        print(
            "Error:",
            e
        )