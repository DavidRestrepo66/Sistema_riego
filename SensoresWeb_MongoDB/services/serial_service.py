from datetime import datetime
from repositories.sensor_repository import SensorRepository

class SerialService:

    @staticmethod
    def process_serial_data(line):

        try:
            temp_dht, hum, temp_bmp, pres, lux = map(
                float,
                line.split(',')
            )

            fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            values = (
                fecha,
                temp_dht,
                hum,
                temp_bmp,
                pres,
                lux
            )

            SensorRepository.save_sensor_data(values)

            return True, values

        except ValueError:
            return False, "Dato inválido"

        except Exception as e:
            return False, str(e)