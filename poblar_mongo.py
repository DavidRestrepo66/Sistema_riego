import sys
from datetime import datetime, timedelta

sys.path.insert(0, 'SensoresWeb_MongoDB')

from pymongo import MongoClient

from config import Config

client = MongoClient(Config.MONGO_URI)

db = client[Config.DATABASE_NAME]

configuraciones_collection = db["configuraciones"]
alertas_collection = db["alertas"]

# ------------------------------------------------------------------
# Limpiar colecciones antes de poblar (evitar duplicados al relanzar)
# ------------------------------------------------------------------
configuraciones_collection.delete_many({})
alertas_collection.delete_many({})

# ------------------------------------------------------------------
# Insertar 3 documentos en "configuraciones" (uno por dispositivo)
# ------------------------------------------------------------------
configuraciones = [
    {
        "id_dispositivo": 1,
        "nombre": "Arduino Norte",
        "horario_riego": {
            "inicio": "06:00",
            "fin": "07:30",
            "dias": ["lunes", "miercoles", "viernes"]
        },
        "alertas_activas": ["humedad", "temp_dht"],
        "umbral_bateria": 20,
        "metadata": {
            "firmware": "v2.1",
            "ultima_calibracion": "2024-11-15"
        }
    },
    {
        "id_dispositivo": 2,
        "nombre": "Arduino Sur",
        "horario_riego": {
            "inicio": "07:00",
            "fin": "08:00",
            "dias": ["martes", "jueves", "sabado"]
        },
        "alertas_activas": ["humedad", "presion"],
        "umbral_bateria": 15,
        "metadata": {
            "firmware": "v2.3",
            "ultima_calibracion": "2024-12-01"
        }
    },
    {
        "id_dispositivo": 3,
        "nombre": "Arduino Invernadero",
        "horario_riego": {
            "inicio": "05:30",
            "fin": "06:30",
            "dias": ["lunes", "martes", "miercoles", "jueves", "viernes"]
        },
        "alertas_activas": ["humedad", "temp_dht", "luz"],
        "umbral_bateria": 25,
        "metadata": {
            "firmware": "v2.5",
            "ultima_calibracion": "2025-01-10"
        }
    }
]

resultado_conf = configuraciones_collection.insert_many(configuraciones)
print(f"Configuraciones insertadas: {len(resultado_conf.inserted_ids)} documentos")

# ------------------------------------------------------------------
# Insertar 12+ documentos en "alertas" con variedad de niveles/zonas
# ------------------------------------------------------------------
ahora = datetime.utcnow()

alertas = [
    # Zona A Tomate — humedad crítica
    {
        "fecha": ahora - timedelta(hours=1),
        "id_zona": 1,
        "zona": "Zona A Tomate",
        "variable": "humedad",
        "valor_medido": 18.5,
        "umbral_superado": 30.0,
        "nivel": "critico",
        "mensaje": "Humedad muy por debajo del mínimo crítico"
    },
    {
        "fecha": ahora - timedelta(hours=3),
        "id_zona": 1,
        "zona": "Zona A Tomate",
        "variable": "temp_dht",
        "valor_medido": 38.4,
        "umbral_superado": 35.0,
        "nivel": "critico",
        "mensaje": "Temperatura extrema detectada"
    },
    {
        "fecha": ahora - timedelta(hours=5),
        "id_zona": 1,
        "zona": "Zona A Tomate",
        "variable": "humedad",
        "valor_medido": 35.2,
        "umbral_superado": 40.0,
        "nivel": "advertencia",
        "mensaje": "Humedad por debajo del mínimo"
    },
    {
        "fecha": ahora - timedelta(hours=8),
        "id_zona": 1,
        "zona": "Zona A Tomate",
        "variable": "luz",
        "valor_medido": 820.0,
        "umbral_superado": 900.0,
        "nivel": "normal",
        "mensaje": "Nivel de luz dentro del rango esperado"
    },
    # Zona B Lechuga — presión y temperatura
    {
        "fecha": ahora - timedelta(hours=2),
        "id_zona": 2,
        "zona": "Zona B Lechuga",
        "variable": "presion",
        "valor_medido": 1025.8,
        "umbral_superado": 1013.0,
        "nivel": "advertencia",
        "mensaje": "Presión atmosférica elevada"
    },
    {
        "fecha": ahora - timedelta(hours=4),
        "id_zona": 2,
        "zona": "Zona B Lechuga",
        "variable": "humedad",
        "valor_medido": 72.1,
        "umbral_superado": 70.0,
        "nivel": "advertencia",
        "mensaje": "Humedad por encima del máximo recomendado"
    },
    {
        "fecha": ahora - timedelta(hours=6),
        "id_zona": 2,
        "zona": "Zona B Lechuga",
        "variable": "temp_dht",
        "valor_medido": 22.3,
        "umbral_superado": 30.0,
        "nivel": "normal",
        "mensaje": "Temperatura en rango óptimo"
    },
    {
        "fecha": ahora - timedelta(hours=10),
        "id_zona": 2,
        "zona": "Zona B Lechuga",
        "variable": "humedad",
        "valor_medido": 15.0,
        "umbral_superado": 30.0,
        "nivel": "critico",
        "mensaje": "Sequedad crítica detectada en Zona B"
    },
    # Zona C Pimiento — variedad mixta
    {
        "fecha": ahora - timedelta(hours=1, minutes=30),
        "id_zona": 3,
        "zona": "Zona C Pimiento",
        "variable": "temp_dht",
        "valor_medido": 36.9,
        "umbral_superado": 35.0,
        "nivel": "critico",
        "mensaje": "Temperatura peligrosa para el pimiento"
    },
    {
        "fecha": ahora - timedelta(hours=7),
        "id_zona": 3,
        "zona": "Zona C Pimiento",
        "variable": "humedad",
        "valor_medido": 42.5,
        "umbral_superado": 40.0,
        "nivel": "normal",
        "mensaje": "Humedad estable en Zona C"
    },
    {
        "fecha": ahora - timedelta(hours=9),
        "id_zona": 3,
        "zona": "Zona C Pimiento",
        "variable": "luz",
        "valor_medido": 1100.0,
        "umbral_superado": 1000.0,
        "nivel": "advertencia",
        "mensaje": "Radiación solar elevada"
    },
    {
        "fecha": ahora - timedelta(hours=12),
        "id_zona": 3,
        "zona": "Zona C Pimiento",
        "variable": "presion",
        "valor_medido": 998.4,
        "umbral_superado": 1000.0,
        "nivel": "normal",
        "mensaje": "Presión dentro del rango normal"
    },
    {
        "fecha": ahora - timedelta(hours=15),
        "id_zona": 1,
        "zona": "Zona A Tomate",
        "variable": "luz",
        "valor_medido": 250.0,
        "umbral_superado": 400.0,
        "nivel": "advertencia",
        "mensaje": "Luz insuficiente para fotosíntesis óptima"
    },
    {
        "fecha": ahora - timedelta(hours=20),
        "id_zona": 2,
        "zona": "Zona B Lechuga",
        "variable": "temp_dht",
        "valor_medido": 12.0,
        "umbral_superado": 15.0,
        "nivel": "critico",
        "mensaje": "Temperatura por debajo del mínimo crítico nocturno"
    }
]

resultado_alertas = alertas_collection.insert_many(alertas)
print(f"Alertas insertadas: {len(resultado_alertas.inserted_ids)} documentos")

print("\nPoblado de MongoDB completado exitosamente.")
print(f"  - Coleccion 'configuraciones': {configuraciones_collection.count_documents({})} documentos")
print(f"  - Coleccion 'alertas':         {alertas_collection.count_documents({})} documentos")
