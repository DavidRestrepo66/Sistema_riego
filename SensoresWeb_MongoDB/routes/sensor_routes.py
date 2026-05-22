from flask import (
    Blueprint,
    jsonify
)

from services.sensor_service import (
    SensorService
)

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