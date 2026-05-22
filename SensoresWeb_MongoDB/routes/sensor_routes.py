import random
from datetime import datetime

from flask import (
    Blueprint,
    jsonify,
    request
)

from services.sensor_service import (
    SensorService
)

from utils.sql_server import (
    get_sql_server_connection
)

from utils.decorators import login_required

sensor_bp = Blueprint(
    "sensor",
    __name__
)

@sensor_bp.route("/api/datos")
def api_datos():

    datos = SensorService.obtener_datos()

    resultado = []

    for d in datos:

        resultado.append({

            "id": str(d["_id"]),

            "fecha": str(d["fecha"]),

            "temp_dht": d["temp_dht"],

            "humedad": d["humedad"],

            "temp_bmp": d["temp_bmp"],

            "presion": d["presion"],

            "luz": d["luz"]
        })

    return jsonify(resultado)


@sensor_bp.route("/api/simular", methods=["POST"])
@login_required
def api_simular():

    try:
        n = min(int(request.json.get("n", 1)), 10) if request.is_json else 1
    except (ValueError, TypeError):
        n = 1

    id_dispositivo = 1
    id_zona = 1

    mongo_ok = 0
    sql_ok = 0
    mongo_error = None
    sql_error = None

    for _ in range(n):

        temp_dht = round(random.uniform(18.0, 35.0), 1)

        lectura = {
            "fecha":    datetime.now(),
            "temp_dht": temp_dht,
            "humedad":  round(random.uniform(30.0, 80.0), 1),
            "temp_bmp": round(temp_dht + random.uniform(-0.5, 0.5), 1),
            "presion":  round(random.uniform(1005.0, 1025.0), 1),
            "luz":      round(random.uniform(100.0, 1000.0), 1),
        }

        try:
            SensorService.guardar_lectura(lectura)
            mongo_ok += 1
        except Exception as e:
            mongo_error = str(e)

        try:
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
                    id_dispositivo,
                    id_zona,
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
            sql_ok += 1
        except Exception as e:
            sql_error = str(e)

    return jsonify({
        "n":          n,
        "mongo":      {"ok": mongo_ok, "error": mongo_error},
        "sql":        {"ok": sql_ok,   "error": sql_error},
    })