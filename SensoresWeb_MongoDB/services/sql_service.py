from repositories.sql_repository import SqlRepository


class SqlService:

    @staticmethod
    def get_resumen_zonas():

        return SqlRepository.get_resumen_zonas()

    @staticmethod
    def get_lecturas_zona(id_zona):

        return SqlRepository.get_lecturas_zona(id_zona)

    @staticmethod
    def clasificar_humedad(valor):

        return SqlRepository.clasificar_humedad(valor)
