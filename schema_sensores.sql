-- ============================================================
--  schema_sensores.sql
--  Base de Datos 2 - Proyecto Final
--  Sistema IoT de sensores agricolas (Arduino + Flask)
--  Autor: David Restrepo
--  Descripcion: Script completo y autonomo para SQL Server.
--               Crea la BD, tablas, datos de prueba,
--               vista, funcion y procedimiento almacenado.
-- ============================================================


-- ------------------------------------------------------------
-- 1. CREACION DE LA BASE DE DATOS
-- ------------------------------------------------------------

IF EXISTS (SELECT * FROM sys.databases WHERE name = 'sensores')
    DROP DATABASE sensores;
GO

CREATE DATABASE sensores;
GO

USE sensores;
GO


-- ------------------------------------------------------------
-- 2. CREACION DE TABLAS
-- ------------------------------------------------------------

-- Tabla: dispositivos
--   Representa cada dispositivo Arduino instalado en campo.
CREATE TABLE dispositivos (
    id                INT         IDENTITY(1,1) PRIMARY KEY,
    nombre            VARCHAR(100)  NOT NULL,
    ubicacion         VARCHAR(200),
    tipo              VARCHAR(50),
    fecha_instalacion DATE
);
GO

-- Tabla: zonas_riego
--   Define las zonas agricolas donde se ubican los dispositivos.
CREATE TABLE zonas_riego (
    id           INT          IDENTITY(1,1) PRIMARY KEY,
    nombre       VARCHAR(100)  NOT NULL,
    tipo_cultivo VARCHAR(100),
    descripcion  VARCHAR(300)
);
GO

-- Tabla: lecturas
--   Almacena cada lectura de sensores enviada por el Arduino.
CREATE TABLE lecturas (
    id            INT      IDENTITY(1,1) PRIMARY KEY,
    id_dispositivo INT     NOT NULL,
    id_zona        INT     NOT NULL,
    fecha         DATETIME NOT NULL,
    temp_dht      FLOAT,
    humedad       FLOAT,
    temp_bmp      FLOAT,
    presion       FLOAT,
    luz           FLOAT,
    CONSTRAINT fk_lecturas_dispositivo FOREIGN KEY (id_dispositivo)
        REFERENCES dispositivos(id),
    CONSTRAINT fk_lecturas_zona        FOREIGN KEY (id_zona)
        REFERENCES zonas_riego(id)
);
GO

-- Tabla: umbrales_alerta
--   Define valores minimos y maximos aceptables por zona y variable.
CREATE TABLE umbrales_alerta (
    id         INT         IDENTITY(1,1) PRIMARY KEY,
    id_zona    INT         NOT NULL,
    variable   VARCHAR(50) NOT NULL,
    valor_min  FLOAT,
    valor_max  FLOAT,
    activo     BIT         NOT NULL DEFAULT 1,
    CONSTRAINT fk_umbrales_zona FOREIGN KEY (id_zona)
        REFERENCES zonas_riego(id)
);
GO


-- ------------------------------------------------------------
-- 3. DATOS DE PRUEBA
-- ------------------------------------------------------------

-- 3.1 Dispositivos (3 filas)
INSERT INTO dispositivos (nombre, ubicacion, tipo, fecha_instalacion)
VALUES
    ('Arduino-01', 'Invernadero Norte',   'DHT22/BMP280/LDR', '2024-01-15'),
    ('Arduino-02', 'Campo Abierto Este',  'DHT22/BMP280/LDR', '2024-02-20'),
    ('Arduino-03', 'Invernadero Sur',     'DHT22/BMP280/LDR', '2024-03-10');
GO

-- 3.2 Zonas de riego (3 filas)
INSERT INTO zonas_riego (nombre, tipo_cultivo, descripcion)
VALUES
    ('Zona A', 'Tomate',    'Invernadero principal con sistema de riego por goteo'),
    ('Zona B', 'Lechuga',   'Campo abierto con riego por aspersion'),
    ('Zona C', 'Pimiento',  'Invernadero secundario con control de humedad automatico');
GO

-- 3.3 Lecturas (18 filas distribuidas entre dispositivos y zonas)
--     Se usa DATEADD para generar marcas de tiempo variadas.
DECLARE @base DATETIME = '2024-04-01 08:00:00';

INSERT INTO lecturas (id_dispositivo, id_zona, fecha, temp_dht, humedad, temp_bmp, presion, luz)
VALUES
    -- Dispositivo 1 - Zona A (6 lecturas)
    (1, 1, DATEADD(HOUR,  0, @base), 22.5, 65.3, 22.1, 1013.2, 420.0),
    (1, 1, DATEADD(HOUR,  6, @base), 24.8, 60.1, 24.5, 1012.8, 850.5),
    (1, 1, DATEADD(HOUR, 12, @base), 27.3, 55.7, 27.0, 1012.5, 980.0),
    (1, 1, DATEADD(HOUR, 18, @base), 25.1, 58.4, 24.9, 1012.9, 310.0),
    (1, 1, DATEADD(HOUR, 24, @base), 21.9, 67.2, 21.6, 1013.5, 200.0),
    (1, 1, DATEADD(HOUR, 30, @base), 23.4, 63.8, 23.1, 1013.1, 760.0),

    -- Dispositivo 2 - Zona B (6 lecturas)
    (2, 2, DATEADD(HOUR,  2, @base), 19.8, 72.5, 19.5, 1014.0, 350.0),
    (2, 2, DATEADD(HOUR,  8, @base), 22.1, 68.9, 21.8, 1013.7, 870.0),
    (2, 2, DATEADD(HOUR, 14, @base), 25.6, 62.3, 25.3, 1013.2, 995.0),
    (2, 2, DATEADD(HOUR, 20, @base), 23.0, 66.1, 22.7, 1013.4, 280.0),
    (2, 2, DATEADD(HOUR, 26, @base), 18.5, 75.8, 18.2, 1014.3, 180.0),
    (2, 2, DATEADD(HOUR, 32, @base), 20.9, 70.4, 20.6, 1013.9, 720.0),

    -- Dispositivo 3 - Zona C (6 lecturas)
    (3, 3, DATEADD(HOUR,  4, @base), 26.2, 45.1, 25.9, 1012.0, 530.0),
    (3, 3, DATEADD(HOUR, 10, @base), 29.4, 38.7, 29.1, 1011.5, 920.0),
    (3, 3, DATEADD(HOUR, 16, @base), 31.8, 35.2, 31.5, 1011.0, 1000.0),
    (3, 3, DATEADD(HOUR, 22, @base), 28.5, 40.6, 28.2, 1011.8, 400.0),
    (3, 3, DATEADD(HOUR, 28, @base), 24.7, 50.3, 24.4, 1012.3, 220.0),
    (3, 3, DATEADD(HOUR, 34, @base), 27.1, 43.9, 26.8, 1012.1, 810.0);
GO

-- 3.4 Umbrales de alerta (6 filas: 2 por zona)
INSERT INTO umbrales_alerta (id_zona, variable, valor_min, valor_max, activo)
VALUES
    -- Zona A - Tomate
    (1, 'humedad',  50.0, 75.0, 1),
    (1, 'temp_dht', 18.0, 30.0, 1),

    -- Zona B - Lechuga
    (2, 'humedad',  60.0, 80.0, 1),
    (2, 'temp_dht', 15.0, 25.0, 1),

    -- Zona C - Pimiento
    (3, 'humedad',  40.0, 65.0, 1),
    (3, 'temp_dht', 20.0, 32.0, 1);
GO


-- ------------------------------------------------------------
-- 4. OBJETOS AVANZADOS
-- ------------------------------------------------------------

-- 4.1 VISTA: vista_resumen_por_zona
--     Resume promedios de cada combinacion zona-dispositivo.

IF OBJECT_ID('dbo.vista_resumen_por_zona', 'V') IS NOT NULL
    DROP VIEW dbo.vista_resumen_por_zona;
GO

CREATE VIEW dbo.vista_resumen_por_zona AS
SELECT
    z.nombre                  AS zona,
    d.nombre                  AS dispositivo,
    COUNT(l.id)               AS total_lecturas,
    AVG(l.temp_dht)           AS prom_temp,
    AVG(l.humedad)            AS prom_humedad,
    AVG(l.presion)            AS prom_presion,
    AVG(l.luz)                AS prom_luz
FROM lecturas       l
INNER JOIN zonas_riego   z ON l.id_zona        = z.id
INNER JOIN dispositivos  d ON l.id_dispositivo = d.id
GROUP BY z.nombre, d.nombre;
GO


-- 4.2 FUNCION: dbo.fn_clasificar_humedad
--     Clasifica un valor de humedad en SECA / OPTIMA / EXCESO.

IF OBJECT_ID('dbo.fn_clasificar_humedad', 'FN') IS NOT NULL
    DROP FUNCTION dbo.fn_clasificar_humedad;
GO

CREATE FUNCTION dbo.fn_clasificar_humedad (@humedad FLOAT)
RETURNS VARCHAR(20)
AS
BEGIN
    DECLARE @clasificacion VARCHAR(20);

    IF @humedad < 40
        SET @clasificacion = 'SECA';
    ELSE IF @humedad <= 70
        SET @clasificacion = 'OPTIMA';
    ELSE
        SET @clasificacion = 'EXCESO';

    RETURN @clasificacion;
END;
GO


-- 4.3 PROCEDIMIENTO ALMACENADO: sp_lecturas_por_zona
--     Retorna las 10 lecturas mas recientes de una zona dada.

IF OBJECT_ID('dbo.sp_lecturas_por_zona', 'P') IS NOT NULL
    DROP PROCEDURE dbo.sp_lecturas_por_zona;
GO

CREATE PROCEDURE dbo.sp_lecturas_por_zona
    @id_zona INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT TOP 10
        l.id                          AS id_lectura,
        z.nombre                      AS zona,
        d.nombre                      AS dispositivo,
        l.fecha,
        l.temp_dht,
        l.humedad,
        l.temp_bmp,
        l.presion,
        l.luz
    FROM lecturas       l
    INNER JOIN zonas_riego   z ON l.id_zona        = z.id
    INNER JOIN dispositivos  d ON l.id_dispositivo = d.id
    WHERE l.id_zona = @id_zona
    ORDER BY l.fecha DESC;
END;
GO


-- ------------------------------------------------------------
-- 5. CONSULTAS DE PRUEBA
-- ------------------------------------------------------------

-- 5.1 Resumen por zona (vista)
SELECT * FROM dbo.vista_resumen_por_zona;
GO

-- 5.2 Ultimas 10 lecturas de la Zona A (id = 1)
EXEC dbo.sp_lecturas_por_zona 1;
GO

-- 5.3 Clasificar una humedad de ejemplo
SELECT dbo.fn_clasificar_humedad(55.0) AS clasificacion_humedad;
GO

-- 5.4 Subconsulta avanzada:
--     Dispositivos cuya temperatura promedio supera
--     el promedio general de todas las lecturas.
SELECT
    d.nombre                          AS dispositivo,
    AVG(l.temp_dht)                   AS prom_temp_dispositivo,
    (SELECT AVG(temp_dht) FROM lecturas) AS prom_temp_global
FROM lecturas      l
INNER JOIN dispositivos d ON l.id_dispositivo = d.id
GROUP BY d.id, d.nombre
HAVING AVG(l.temp_dht) > (SELECT AVG(temp_dht) FROM lecturas)
ORDER BY prom_temp_dispositivo DESC;
GO
