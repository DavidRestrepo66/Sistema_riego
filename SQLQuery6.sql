/* CREACIÓN DE LA BASE DE DATOS

   Esta base de datos almacenará las lecturas de sensores
   provenientes del sistema IoT desarrollado con Flask,
   Arduino y MongoDB.


CREATE DATABASE sensores;
GO
*/
USE sensores;
GO

/*
 TABLA: lecturas

   Esta tabla almacena las lecturas de sensores:
   - temperatura
   - humedad
   - presión
   - intensidad de luz

   Cada registro representa una lectura capturada
   desde el Arduino.


CREATE TABLE lecturas (

    id INT IDENTITY(1,1) PRIMARY KEY,

    fecha DATETIME,

    temp_dht FLOAT,

    humedad FLOAT,

    temp_bmp FLOAT,

    presion FLOAT,

    luz FLOAT

);
GO


 VISTA: vista_promedios

   Esta vista calcula automáticamente los promedios
   generales de:
   - temperatura
   - humedad
   - presión
   - luz

   Permite realizar análisis rápidos sin repetir
   consultas complejas.


CREATE VIEW vista_promedios AS

SELECT

    AVG(temp_dht) AS promedio_temperatura,

    AVG(humedad) AS promedio_humedad,

    AVG(presion) AS promedio_presion,

    AVG(luz) AS promedio_luz

FROM lecturas;
GO


 FUNCIÓN: fn_temperatura_alta

   Esta función evalúa una temperatura y devuelve:
   - 'ALTA' si la temperatura supera 30 grados
   - 'NORMAL' en caso contrario

   Se utiliza para clasificar temperaturas.


CREATE FUNCTION fn_temperatura_alta(

    @temp FLOAT

)

RETURNS VARCHAR(20)

AS
BEGIN

    DECLARE @resultado VARCHAR(20)

    IF @temp > 30
        SET @resultado = 'ALTA'

    ELSE
        SET @resultado = 'NORMAL'

    RETURN @resultado

END
GO


  S PROCEDIMIENTO ALMACENADO: sp_ultimas_lecturas

   Este procedimiento almacenado obtiene las
   últimas 10 lecturas registradas en el sistema.

   Los datos se ordenan desde el más reciente
   hasta el más antiguo.


CREATE PROCEDURE sp_ultimas_lecturas

AS
BEGIN

    SELECT TOP 10 *

    FROM lecturas

    ORDER BY fecha DESC

END
GO
*/

/* PRUEBA DE LA FUNCIÓN */

SELECT dbo.fn_temperatura_alta(35);
GO


/* PRUEBA DE LA VISTA */

SELECT * FROM vista_promedios;
GO


/* PRUEBA DEL PROCEDIMIENTO ALMACENADO */

EXEC sp_ultimas_lecturas;
GO