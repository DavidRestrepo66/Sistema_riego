# Integración SQL Server + MongoDB — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Completar el proyecto final de Bases de Datos 2 cubriendo los 5 criterios de evaluación (5.0 puntos) integrando correctamente SQL Server y MongoDB en la app Flask existente.

**Architecture:** La app Flask actúa como capa intermedia entre dos motores: SQL Server maneja el modelo relacional-analítico (4 tablas, vistas, SP, función) y MongoDB el dominio flexible (configuraciones de dispositivos, log de alertas, usuarios). Cada motor tiene un rol diferenciado — no duplican datos.

**Tech Stack:** Flask · Python · pyodbc (SQL Server) · pymongo (MongoDB Atlas) · Jinja2 · ODBC Driver 17

---

## Mapa de archivos

| Acción | Archivo | Responsabilidad |
|--------|---------|-----------------|
| Crear | `schema_sensores.sql` | Script SQL limpio y ejecutable: tablas, datos, vista, función, SP |
| Modificar | `SQLQuery6.sql` | Dejar solo como referencia histórica (ya no es el script principal) |
| Crear | `SensoresWeb_MongoDB/repositories/sql_repository.py` | Acceso a SQL Server: vista, SP, función |
| Crear | `SensoresWeb_MongoDB/services/sql_service.py` | Lógica de negocio SQL |
| Crear | `SensoresWeb_MongoDB/routes/sql_routes.py` | Endpoints `/api/sql/*` |
| Modificar | `SensoresWeb_MongoDB/utils/sql_server.py` | Agregar parámetros desde .env |
| Crear | `SensoresWeb_MongoDB/templates/analisis.html` | Página que muestra datos de SQL Server |
| Modificar | `SensoresWeb_MongoDB/templates/dashboard.html` | Agregar enlace a /analisis |
| Modificar | `SensoresWeb_MongoDB/utils/db.py` | Agregar colecciones configuraciones y alertas |
| Modificar | `SensoresWeb_MongoDB/app.py` | Registrar sql_bp |
| Crear | `SensoresWeb_MongoDB/config.py` | Leer credenciales desde .env |
| Crear | `.env` | Variables de entorno (no se sube al repo) |
| Crear | `.gitignore` | Excluir .env y __pycache__ |
| Crear | `exportar_mongo.py` | Script que exporta colecciones a JSON |
| Crear | `mongo_export/` | Carpeta con los JSON exportados |

---

## Fase 1 — Rediseño SQL Server: modelo relacional (Criterio 1)

### Tarea 1.1: Definir el nuevo esquema de 4 tablas

**Archivos:**
- Crear: `schema_sensores.sql`

**Modelo de tablas:**

```
dispositivos
  id           INT IDENTITY PK
  nombre       VARCHAR(100)
  ubicacion    VARCHAR(200)
  tipo         VARCHAR(50)      -- 'Arduino UNO', 'ESP32', etc.
  fecha_inst   DATE

zonas_riego
  id           INT IDENTITY PK
  nombre       VARCHAR(100)
  tipo_cultivo VARCHAR(100)
  descripcion  VARCHAR(300)

lecturas
  id           INT IDENTITY PK
  id_dispositivo INT FK → dispositivos.id
  id_zona        INT FK → zonas_riego.id
  fecha          DATETIME
  temp_dht       FLOAT
  humedad        FLOAT
  temp_bmp       FLOAT
  presion        FLOAT
  luz            FLOAT

umbrales_alerta
  id           INT IDENTITY PK
  id_zona      INT FK → zonas_riego.id
  variable     VARCHAR(50)   -- 'humedad', 'temp_dht', 'presion', 'luz'
  valor_min    FLOAT
  valor_max    FLOAT
  activo       BIT DEFAULT 1
```

**Por qué este diseño:** `lecturas` ya existe con esos 5 campos — solo se le añaden 2 FKs. `dispositivos` y `zonas_riego` dan el contexto relacional que faltaba. `umbrales_alerta` introduce una cuarta tabla con FK y semántica de negocio real (riego), lo que permite JOINs naturales en la vista y el SP.

- [ ] **Paso 1.1.1:** Crear `schema_sensores.sql` con `CREATE DATABASE sensores; GO` (ejecutable, sin comentar bloques de código)
- [ ] **Paso 1.1.2:** Agregar `CREATE TABLE dispositivos` con PK y campos listados arriba
- [ ] **Paso 1.1.3:** Agregar `CREATE TABLE zonas_riego` con PK y campos listados arriba
- [ ] **Paso 1.1.4:** Agregar `CREATE TABLE lecturas` con PK + 2 FKs (id_dispositivo, id_zona) y los 5 campos de sensor
- [ ] **Paso 1.1.5:** Agregar `CREATE TABLE umbrales_alerta` con PK + FK a zonas_riego

### Tarea 1.2: Insertar datos de prueba coherentes

- [ ] **Paso 1.2.1:** Insertar 3 registros en `dispositivos` (ej. "Arduino Zona Norte", "Arduino Zona Sur", "Arduino Invernadero")
- [ ] **Paso 1.2.2:** Insertar 3 registros en `zonas_riego` (ej. "Zona Norte" — tomate, "Zona Sur" — lechuga, "Invernadero" — orquídeas)
- [ ] **Paso 1.2.3:** Insertar 15+ registros en `lecturas` distribuidos entre los 3 dispositivos y 3 zonas con fechas variadas
- [ ] **Paso 1.2.4:** Insertar 6+ registros en `umbrales_alerta` (2 por zona: umbrales de humedad y temperatura)

---

## Fase 2 — Elementos avanzados SQL Server (Criterio 2)

### Tarea 2.1: Vista con JOIN y GROUP BY

**Vista:** `vista_resumen_por_zona`

Hace JOIN entre `lecturas`, `zonas_riego` y `dispositivos`. Agrupa por zona y calcula promedios de temperatura, humedad, presión y luz. También cuenta cuántas lecturas hay por zona. Usa `GROUP BY z.nombre`.

- [ ] **Paso 2.1.1:** Escribir `CREATE VIEW vista_resumen_por_zona AS SELECT z.nombre AS zona, d.nombre AS dispositivo, COUNT(*) AS total_lecturas, AVG(l.temp_dht) AS prom_temp, AVG(l.humedad) AS prom_humedad, AVG(l.presion) AS prom_presion, AVG(l.luz) AS prom_luz FROM lecturas l JOIN zonas_riego z ON l.id_zona = z.id JOIN dispositivos d ON l.id_dispositivo = d.id GROUP BY z.nombre, d.nombre`
- [ ] **Paso 2.1.2:** Probar la vista con `SELECT * FROM vista_resumen_por_zona`

### Tarea 2.2: Función escalar con lógica de dominio

**Función:** `fn_clasificar_humedad(@humedad FLOAT) RETURNS VARCHAR(20)`

Devuelve 'SECA' (< 40), 'OPTIMA' (40–70), 'EXCESO' (> 70). Se usará desde la app al mostrar análisis.

- [ ] **Paso 2.2.1:** Escribir `CREATE FUNCTION dbo.fn_clasificar_humedad(@humedad FLOAT) RETURNS VARCHAR(20) AS BEGIN ... END`
- [ ] **Paso 2.2.2:** Probar con `SELECT dbo.fn_clasificar_humedad(55.0)` — debe retornar 'OPTIMA'

### Tarea 2.3: Procedimiento almacenado con parámetro y JOIN

**SP:** `sp_lecturas_por_zona(@id_zona INT)`

Recibe un id de zona, devuelve las últimas 10 lecturas de esa zona con el nombre del dispositivo (JOIN lecturas + dispositivos + zonas_riego). Usa `ORDER BY fecha DESC`.

- [ ] **Paso 2.3.1:** Escribir `CREATE PROCEDURE sp_lecturas_por_zona @id_zona INT AS BEGIN SELECT TOP 10 ... FROM lecturas l JOIN dispositivos d ON ... JOIN zonas_riego z ON ... WHERE l.id_zona = @id_zona ORDER BY l.fecha DESC END`
- [ ] **Paso 2.3.2:** Probar con `EXEC sp_lecturas_por_zona 1` — debe retornar filas de la primera zona

### Tarea 2.4: Subconsulta avanzada (bonus que refuerza Criterio 2)

Añadir al final del script una consulta que use subconsulta: dispositivos cuya temperatura promedio supera el promedio general de todos los dispositivos. Esta consulta va en el script SQL como ejemplo de consulta avanzada.

- [ ] **Paso 2.4.1:** Escribir la consulta con subconsulta en el script (no en vista, solo como ejemplo ejecutable al final)

---

## Fase 3 — Capa de integración SQL en la app web (Criterio 3)

### Tarea 3.1: Repositorio SQL

**Archivo:** `SensoresWeb_MongoDB/repositories/sql_repository.py`

Clase `SqlRepository` con 3 métodos estáticos:
- `get_resumen_zonas()` → ejecuta `SELECT * FROM vista_resumen_por_zona` y retorna lista de dicts
- `get_lecturas_zona(id_zona)` → ejecuta `EXEC sp_lecturas_por_zona ?` con pyodbc y retorna lista de dicts
- `clasificar_humedad(valor)` → ejecuta `SELECT dbo.fn_clasificar_humedad(?)` y retorna el string resultado

Cada método abre conexión con `get_sql_server_connection()`, ejecuta, cierra y retorna.

- [ ] **Paso 3.1.1:** Crear el archivo con los 3 métodos estáticos
- [ ] **Paso 3.1.2:** Ejecutar `python test_sql.py` (ya existe) para verificar conexión base

### Tarea 3.2: Servicio SQL

**Archivo:** `SensoresWeb_MongoDB/services/sql_service.py`

Clase `SqlService` que delega a `SqlRepository`. Mismos 3 métodos, sin lógica adicional. Siguiendo el patrón ya existente en `sensor_service.py`.

- [ ] **Paso 3.2.1:** Crear el archivo con la clase `SqlService` delegando a `SqlRepository`

### Tarea 3.3: Rutas SQL y template de análisis

**Archivos:**
- Crear: `SensoresWeb_MongoDB/routes/sql_routes.py`
- Crear: `SensoresWeb_MongoDB/templates/analisis.html`

**Rutas a crear:**
- `GET /api/sql/resumen` → devuelve JSON con `SqlService.get_resumen_zonas()`
- `GET /api/sql/zona/<int:id_zona>` → devuelve JSON con `SqlService.get_lecturas_zona(id_zona)`
- `GET /api/sql/humedad/<float:valor>` → devuelve JSON con `{"clasificacion": SqlService.clasificar_humedad(valor)}`

**Template `analisis.html`:** Página HTML que carga `/api/sql/resumen` con fetch y muestra una tabla con columnas zona / dispositivo / total lecturas / prom temperatura / prom humedad. Incluye un campo de input para ingresar un valor de humedad y mostrar la clasificación via `/api/sql/humedad/<valor>`. También un selector de zona para cargar las últimas lecturas via `/api/sql/zona/<id>`.

- [ ] **Paso 3.3.1:** Crear `sql_routes.py` con los 3 endpoints y el `sql_bp = Blueprint('sql', __name__)`
- [ ] **Paso 3.3.2:** Crear `analisis.html` con la tabla de resumen y los controles interactivos
- [ ] **Paso 3.3.3:** Registrar `sql_bp` en `app.py` con `app.register_blueprint(sql_bp)`
- [ ] **Paso 3.3.4:** Agregar enlace a `/analisis` en `dashboard.html` (ya existe la ruta en `view_routes.py`)
- [ ] **Paso 3.3.5:** Verificar manualmente que `/analisis` carga y muestra datos reales de SQL Server

### Tarea 3.4: Adaptar guardar_datos.py a nuevo esquema

`guardar_datos.py` inserta en la tabla `lecturas` que ahora requiere `id_dispositivo` e `id_zona`. Hay que definir valores fijos (ej. dispositivo 1, zona 1) para el Arduino físico, o pasar como constante configurable.

- [ ] **Paso 3.4.1:** Agregar `ID_DISPOSITIVO = 1` e `ID_ZONA = 1` en `config.py`
- [ ] **Paso 3.4.2:** Actualizar el INSERT en `guardar_datos.py` para incluir esos dos campos

---

## Fase 4 — Replantear MongoDB para que complemente SQL Server (Criterio 4)

### Tarea 4.1: Definir el rol diferenciado de MongoDB

SQL Server tiene: datos de sensores estructurados, relaciones entre dispositivos y zonas, umbrales fijos.
MongoDB tendrá: configuraciones flexibles por dispositivo (esquema variable, fácil de cambiar), log de alertas (documentos ricos con contexto variable), y usuarios (ya existe).

**Colecciones finales:**
1. `usuarios` — ya existe, para autenticación
2. `lecturas` — ya existe, ingesta cruda de sensores (conservar como buffer de tiempo real)
3. `configuraciones` — nueva, documentos tipo `{id_dispositivo: 1, nombre: "Arduino Norte", horario_riego: {...}, alertas_activas: [...], metadata: {...}}` — esquema flexible por dispositivo
4. `alertas` — nueva, log de eventos `{fecha, id_zona, variable, valor_medido, umbral_superado, nivel: "critico/advertencia", mensaje}`

- [ ] **Paso 4.1.1:** Actualizar `utils/db.py` para exportar `configuraciones_collection` y `alertas_collection`

### Tarea 4.2: Poblar las nuevas colecciones con documentos de prueba

- [ ] **Paso 4.2.1:** Crear `poblar_mongo.py` — script que inserta 3 documentos en `configuraciones` (uno por dispositivo) y 10+ documentos en `alertas` (variados por zona, variable y nivel)
- [ ] **Paso 4.2.2:** Ejecutar `poblar_mongo.py` y verificar en MongoDB Atlas que los datos aparecen

### Tarea 4.3: Exponer datos de MongoDB en la app

Agregar a `sensor_routes.py` (o en `sql_routes.py`) dos endpoints:
- `GET /api/mongo/alertas` → devuelve las últimas 20 alertas de la colección `alertas`
- `GET /api/mongo/configuraciones` → devuelve todas las configuraciones

Agregar una sección en `analisis.html` que muestre el log de alertas de Mongo junto al resumen de SQL. Así una sola página demuestra integración de ambos motores.

- [ ] **Paso 4.3.1:** Crear `repositories/mongo_extra_repository.py` con métodos `get_alertas()` y `get_configuraciones()`
- [ ] **Paso 4.3.2:** Agregar los 2 endpoints en `sql_routes.py`
- [ ] **Paso 4.3.3:** Agregar sección de alertas en `analisis.html` consumiendo `/api/mongo/alertas`

---

## Fase 5 — Seguridad y limpieza

### Tarea 5.1: Mover credenciales a .env

- [ ] **Paso 5.1.1:** Crear `.env` con `SECRET_KEY`, `MONGO_URI`, `DATABASE_NAME`, `SQL_SERVER`, `SQL_DATABASE`
- [ ] **Paso 5.1.2:** Reescribir `config.py` para leer con `python-dotenv` (`os.getenv(...)`)
- [ ] **Paso 5.1.3:** Crear `.gitignore` que excluya `.env`, `__pycache__/`, `*.pyc`, `mongo_export/`
- [ ] **Paso 5.1.4:** Actualizar `utils/sql_server.py` para leer SERVER y DATABASE de `Config`

### Tarea 5.2: Unificar nombre de base de datos SQL

El server name actualmente es `FelipeSalda\\SQLEXPRESS` (hardcodeado). El nombre de BD varía entre `sensores`, `sensores_sql`. Unificar a `sensores` en `.env`.

- [ ] **Paso 5.2.1:** El script `schema_sensores.sql` usa `CREATE DATABASE sensores; USE sensores;`
- [ ] **Paso 5.2.2:** `.env` tiene `SQL_DATABASE=sensores`
- [ ] **Paso 5.2.3:** `SQLQuery7,vista.sql` queda como archivo legacy sin uso activo

---

## Fase 6 — Entregables (requisito del PDF)

### Tarea 6.1: Script SQL ejecutable y limpio

- [ ] **Paso 6.1.1:** Verificar que `schema_sensores.sql` corre de inicio a fin sin errores (DROP IF EXISTS + CREATE + INSERT + CREATE VIEW/FUNCTION/PROCEDURE)
- [ ] **Paso 6.1.2:** Añadir al final las 3 pruebas: `SELECT * FROM vista_resumen_por_zona`, `EXEC sp_lecturas_por_zona 1`, `SELECT dbo.fn_clasificar_humedad(55.0)`

### Tarea 6.2: Exportar colecciones MongoDB a JSON

- [ ] **Paso 6.2.1:** Crear `exportar_mongo.py` — script Python que conecta a Atlas, itera las 4 colecciones y escribe un archivo JSON por colección en `mongo_export/`
- [ ] **Paso 6.2.2:** Ejecutar el script y verificar que genera `mongo_export/usuarios.json`, `mongo_export/lecturas.json`, `mongo_export/configuraciones.json`, `mongo_export/alertas.json`

### Tarea 6.3: Guion para presentación técnica

- [ ] **Paso 6.3.1:** Crear `docs/presentacion_guion.md` con:
  - Diagrama de arquitectura en texto (Flask ↔ SQL Server + MongoDB)
  - Descripción de cada tabla SQL con su rol en el dominio
  - Descripción de cada colección Mongo y por qué complementa (no duplica) SQL
  - Demo script: mostrar dashboard → analisis → tabla vista SQL → ejecución SP → clasificación función → sección alertas Mongo
  - 3 preguntas técnicas probables y sus respuestas: "¿por qué dos motores?", "¿qué hace la vista?", "¿cómo llama el SP desde Python?"

---

## Verificación final de cobertura del rubric

| Criterio PDF | Cubierto por | Estado |
|---|---|---|
| C1: 4 tablas, PKs, FKs, datos, integridad referencial | Fase 1 — `schema_sensores.sql` | Planificado |
| C2: Vista (con JOIN+GROUP BY) + Función + SP + consulta avanzada | Fase 2 — mismo script | Planificado |
| C3: App consume vista + ejecuta SP + usa función + conexión SQL | Fase 3 — `sql_repository`, `sql_service`, `sql_routes`, `analisis.html` | Planificado |
| C4: Colecciones coherentes + docs suficientes + consulta desde app + complementa SQL | Fase 4 — `configuraciones`, `alertas`, endpoints | Planificado |
| C5: Demo funcionando + explicación técnica + dominio | Fase 6 — guion + sistema funcional completo | Planificado |

**Entregables del PDF:**
- [ ] Script SQL Server → `schema_sensores.sql`
- [ ] Exportación JSON MongoDB → `mongo_export/*.json` (via `exportar_mongo.py`)
- [ ] Código aplicación → `SensoresWeb_MongoDB/` (ya existe, se extiende)
- [ ] Presentación técnica → `docs/presentacion_guion.md`
