from repositories.sensor_repository import (
    SensorRepository
)


class SensorService:

    @staticmethod
    def guardar_lectura(data):

        return SensorRepository.guardar_lectura(
            data
        )

    @staticmethod
    def obtener_datos():

        return SensorRepository.obtener_datos()