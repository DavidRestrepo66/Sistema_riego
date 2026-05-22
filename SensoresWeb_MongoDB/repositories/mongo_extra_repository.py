from utils.db import (
    alertas_collection,
    configuraciones_collection
)


class MongoExtraRepository:

    @staticmethod
    def get_alertas():

        documentos = alertas_collection.find().sort(
            "fecha",
            -1
        ).limit(20)

        resultado = []

        for doc in documentos:

            doc["_id"] = str(doc["_id"])

            resultado.append(doc)

        return resultado

    @staticmethod
    def get_configuraciones():

        documentos = configuraciones_collection.find()

        resultado = []

        for doc in documentos:

            doc["_id"] = str(doc["_id"])

            resultado.append(doc)

        return resultado
