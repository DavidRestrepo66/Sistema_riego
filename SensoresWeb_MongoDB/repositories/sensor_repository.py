from utils.db import (
    lecturas_collection
)


class SensorRepository:

    @staticmethod
    def guardar_lectura(data):

        return lecturas_collection.insert_one(
            data
        )

    @staticmethod
    def obtener_datos():

        datos = lecturas_collection.find().sort(
            "fecha",
            -1
        )

        return list(datos)