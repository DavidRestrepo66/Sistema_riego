from flask import Blueprint, jsonify

from services.sql_service import SqlService

from utils.decorators import login_required

sql_bp = Blueprint('sql', __name__)


@sql_bp.route('/api/sql/resumen')
@login_required
def api_resumen_zonas():

    try:

        datos = SqlService.get_resumen_zonas()

        resultado = []

        for fila in datos:

            resultado.append({
                "zona":         fila["zona"],
                "dispositivo":  fila["dispositivo"],
                "total_lecturas": fila["total_lecturas"],
                "prom_temp":    round(float(fila["prom_temp"]), 2),
                "prom_humedad": round(float(fila["prom_humedad"]), 2),
                "prom_presion": round(float(fila["prom_presion"]), 2),
                "prom_luz":     round(float(fila["prom_luz"]), 2),
            })

        return jsonify(resultado)

    except Exception as e:

        return jsonify({"error": str(e)}), 500


@sql_bp.route('/api/sql/zona/<int:id_zona>')
@login_required
def api_lecturas_zona(id_zona):

    try:

        datos = SqlService.get_lecturas_zona(id_zona)

        resultado = []

        for fila in datos:

            resultado.append({
                "id_lectura":  fila["id_lectura"],
                "zona":        fila["zona"],
                "dispositivo": fila["dispositivo"],
                "fecha":       str(fila["fecha"]),
                "temp_dht":    fila["temp_dht"],
                "humedad":     fila["humedad"],
                "temp_bmp":    fila["temp_bmp"],
                "presion":     fila["presion"],
                "luz":         fila["luz"],
            })

        return jsonify(resultado)

    except Exception as e:

        return jsonify({"error": str(e)}), 500


@sql_bp.route('/api/sql/humedad/<float:valor>')
@login_required
def api_clasificar_humedad(valor):

    try:

        result = SqlService.clasificar_humedad(valor)

        return jsonify({"clasificacion": result, "valor": valor})

    except Exception as e:

        return jsonify({"error": str(e)}), 500
