from utils.sql_server import get_sql_server_connection


class SqlRepository:

    @staticmethod
    def get_resumen_zonas():

        conn = get_sql_server_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                "SELECT * FROM dbo.vista_resumen_por_zona"
            )

            columnas = [col[0] for col in cursor.description]

            filas = cursor.fetchall()

            resultado = [
                dict(zip(columnas, fila))
                for fila in filas
            ]

            return resultado

        except Exception:

            raise

        finally:

            cursor.close()
            conn.close()

    @staticmethod
    def get_lecturas_zona(id_zona: int):

        conn = get_sql_server_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                "EXEC dbo.sp_lecturas_por_zona ?",
                id_zona
            )

            columnas = [col[0] for col in cursor.description]

            filas = cursor.fetchall()

            resultado = [
                dict(zip(columnas, fila))
                for fila in filas
            ]

            return resultado

        except Exception:

            raise

        finally:

            cursor.close()
            conn.close()

    @staticmethod
    def clasificar_humedad(valor: float):

        conn = get_sql_server_connection()

        cursor = conn.cursor()

        try:

            cursor.execute(
                "SELECT dbo.fn_clasificar_humedad(?)",
                valor
            )

            fila = cursor.fetchone()

            return fila[0]

        except Exception:

            raise

        finally:

            cursor.close()
            conn.close()
