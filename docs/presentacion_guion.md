# Guion de Presentación — 3 Estudiantes

**Proyecto:** Sistema de Monitoreo de Sensores IoT — Riego Agrícola
**Bases de Datos 2 · Proyecto Final**
**Duración estimada:** 20 minutos (15 min exposición + 5 min preguntas)

---

## Distribución de roles

| Estudiante | Rol | Tema central | Tiempo |
|:---:|---|---|:---:|
| **A** | Arquitecto | Arquitectura general · MongoDB · Adquisición | 5 min |
| **B** | DBA Relacional | SQL Server · Vista · Función · Procedimiento | 5 min |
| **C** | Full-stack | Flask · Frontend · Demo en vivo | 5 min |
| **Todos** | — | Preguntas y respuestas | 5 min |

> **Tip:** Cada estudiante prepara **su sección + 2 preguntas** del bloque final. Las preguntas no asignadas se las queda quien tenga más afinidad.

---

## 0. Apertura conjunta (30 segundos · todos en pantalla)

**Estudiante A** abre:
> "Buenas tardes. Vamos a presentar nuestro sistema de monitoreo IoT para riego agrícola. Es una aplicación que integra **dos motores de bases de datos** — SQL Server y MongoDB — para resolver problemas distintos del mismo dominio. Lo presentamos en tres bloques: arquitectura, modelo relacional, y la aplicación web."

---

# 🧑‍🎓 PARTE 1 — Estudiante A (Arquitecto)

**Duración: 5 minutos**
**Objetivo:** Que la audiencia entienda el problema, las capas del sistema y el rol de MongoDB.

---

## 1.1 Arquitectura del Sistema (2 min)

Mostrar el diagrama por capas (de `docs/arquitectura.md`):

```
┌─────────────┐
│   Arduino   │  (sensores DHT22, BMP280, LDR)
└──────┬──────┘
       │ Serial (USB)
       ▼
┌─────────────────────┐
│  guardar_datos.py   │  ──┐  (o simular_arduino.py sin hardware)
└─────────────────────┘    │
                           │   doble escritura
            ┌──────────────┴──────────────┐
            ▼                             ▼
   ┌────────────────┐            ┌──────────────────┐
   │   SQL Server   │            │  MongoDB Atlas   │
   │  (relacional)  │            │   (documental)   │
   └────────┬───────┘            └────────┬─────────┘
            │                             │
            └──────────────┬──────────────┘
                           ▼
                  ┌─────────────────┐
                  │  Flask App      │
                  │  routes/        │
                  │  services/      │
                  │  repositories/  │
                  └────────┬────────┘
                           │  HTTP + JSON
                           ▼
                  ┌─────────────────┐
                  │    Navegador    │
                  │   (Jinja2 + JS) │
                  └─────────────────┘
```

**Frases clave para decir:**

> "El sistema tiene cuatro capas. La **adquisición** captura datos del Arduino. La **persistencia** los guarda en dos motores que se complementan. La **aplicación** Flask los expone como API REST. La **presentación** es un dashboard responsive."

> "El patrón clave es **repository**: ninguna ruta toca directamente las bases de datos. Cada motor tiene su repositorio. Si mañana cambiamos MongoDB por PostgreSQL, solo se reescribe ese repositorio."

---

## 1.2 Adquisición y simulador (1 min)

> "El Arduino envía cinco valores cada segundo en formato CSV por puerto serial: temperatura DHT, humedad, temperatura BMP, presión y luz. El script `guardar_datos.py` los parsea y los inserta en **ambas** bases."

> "Para pruebas creamos `simular_arduino.py` y un botón **'Simular Arduino'** en el dashboard que generan datos falsos pero realistas. Esto nos permite probar todo el pipeline sin necesidad del hardware."

**Demostración técnica opcional:** abrir `simular_arduino.py` y mostrar la función `generar_linea_csv()`.

---

## 1.3 MongoDB Atlas — el rol complementario (2 min)

> "MongoDB no es un duplicado de SQL — cumple roles donde SQL es ineficiente."

Mostrar la tabla de colecciones:

| Colección | Rol | ¿Por qué MongoDB y no SQL? |
|-----------|-----|-----------------------------|
| **usuarios** | Autenticación | Puede crecer (roles, preferencias) sin `ALTER TABLE` |
| **lecturas** | Buffer de ingesta | Disponibilidad inmediata aunque SQL esté caído |
| **configuraciones** | Config por dispositivo | Estructura **anidada** (horarios + arrays + metadata) |
| **alertas** | Log de eventos | Cada alerta tiene campos diferentes según la variable |

Mostrar un documento de `configuraciones` (de `docs/bases_de_datos.md`):

```json
{
  "id_dispositivo": 1,
  "nombre": "Arduino Norte",
  "horario_riego": {
    "inicio": "06:00",
    "fin": "07:30",
    "dias": ["lunes", "miercoles", "viernes"]
  },
  "alertas_activas": ["humedad", "temp_dht"],
  "metadata": { "firmware": "v2.1" }
}
```

> "Este documento tiene **objetos anidados y arrays**. Modelarlo en SQL requeriría 3 tablas adicionales con sus FKs. En MongoDB es un solo documento que evoluciona libremente."

---

## 1.4 Transición a parte 2

> "Ahora **Estudiante B** explicará cómo SQL Server estructura el modelo relacional y qué objetos avanzados implementamos."

---

# 🧑‍🎓 PARTE 2 — Estudiante B (DBA Relacional)

**Duración: 5 minutos**
**Objetivo:** Mostrar el modelo ER, los objetos avanzados (vista, función, SP) y cómo se invocan desde Python.

---

## 2.1 Modelo Relacional (1.5 min)

Mostrar el diagrama ER:

```
dispositivos ────────┐
  id (PK)            │
  nombre             │
  ubicacion          │
                     ▼
                 lecturas ──────► zonas_riego
                  id (PK)          id (PK)
                  id_dispositivo   nombre
                  id_zona          tipo_cultivo
                  fecha               │
                  temp_dht            │
                  humedad             │
                  ...                 ▼
                                umbrales_alerta
                                  id_zona (FK)
                                  variable
                                  valor_min/max
```

> "Tenemos cuatro tablas: dos **maestras** (`dispositivos`, `zonas_riego`), una de **hechos** (`lecturas`) y una de **configuración** (`umbrales_alerta`). Las relaciones son uno-a-muchos: una zona tiene muchas lecturas; un dispositivo envía muchas lecturas."

> "Las **FK** garantizan integridad: no se puede insertar una lectura con un `id_dispositivo` que no exista en la tabla maestra. Esta es la ventaja principal de SQL frente a MongoDB para datos estructurados."

---

## 2.2 Vista: `vista_resumen_por_zona` (1 min)

Mostrar el SQL:

```sql
CREATE VIEW dbo.vista_resumen_por_zona AS
SELECT z.nombre AS zona, d.nombre AS dispositivo,
       COUNT(l.id) AS total_lecturas,
       AVG(l.temp_dht) AS prom_temp,
       AVG(l.humedad)  AS prom_humedad
FROM lecturas l
INNER JOIN zonas_riego  z ON l.id_zona        = z.id
INNER JOIN dispositivos d ON l.id_dispositivo = d.id
GROUP BY z.nombre, d.nombre;
```

> "La vista combina las 3 tablas con JOIN, agrupa por zona y dispositivo, y calcula promedios. Desde Python la consultamos **como si fuera una tabla**, pero el JOIN se ejecuta dentro de SQL Server."

```python
cursor.execute("SELECT * FROM dbo.vista_resumen_por_zona")
```

---

## 2.3 Función escalar: `fn_clasificar_humedad` (1 min)

```sql
CREATE FUNCTION dbo.fn_clasificar_humedad (@humedad FLOAT)
RETURNS VARCHAR(20) AS BEGIN
    DECLARE @r VARCHAR(20);
    IF @humedad < 40 SET @r = 'SECA';
    ELSE IF @humedad <= 70 SET @r = 'OPTIMA';
    ELSE SET @r = 'EXCESO';
    RETURN @r;
END;
```

> "La función recibe un número y devuelve una clasificación textual. La lógica de negocio vive **en la base de datos**, no en Python. Cualquier aplicación que consulte esta BD obtiene la misma clasificación."

```python
cursor.execute("SELECT dbo.fn_clasificar_humedad(?)", (55.0,))
```

> "El `?` es un **parámetro vinculado** — pyodbc lo envía separado del SQL, lo que previene inyección SQL."

---

## 2.4 Procedimiento almacenado: `sp_lecturas_por_zona` (1.5 min)

```sql
CREATE PROCEDURE dbo.sp_lecturas_por_zona @id_zona INT
AS BEGIN
    SELECT TOP 10 l.*, d.nombre AS dispositivo, z.nombre AS zona
    FROM lecturas l
    JOIN dispositivos d ON l.id_dispositivo = d.id
    JOIN zonas_riego  z ON l.id_zona = z.id
    WHERE l.id_zona = @id_zona
    ORDER BY l.fecha DESC;
END;
```

> "El procedimiento encapsula una consulta parametrizada. Recibe un `id_zona`, hace JOIN de 3 tablas, ordena por fecha y devuelve las 10 más recientes."

```python
cursor.execute("EXEC dbo.sp_lecturas_por_zona ?", (id_zona,))
```

> "Ventajas vs. hacer la consulta en Python: (1) la lógica vive en la BD y puede cambiarse sin redeployar la app, (2) el plan de ejecución se cachea, (3) los parámetros vinculados previenen inyección SQL."

---

## 2.5 Transición a parte 3

> "Ahora **Estudiante C** mostrará cómo todo esto cobra vida en la aplicación web."

---

# 🧑‍🎓 PARTE 3 — Estudiante C (Full-stack)

**Duración: 5 minutos**
**Objetivo:** Demo en vivo de la aplicación cubriendo login, dashboard, simulador y página de análisis.

---

## 3.1 Estructura de la aplicación Flask (1 min)

Mostrar la organización de carpetas:

```
SensoresWeb_MongoDB/
├── routes/        ← reciben HTTP
├── services/      ← lógica de negocio
├── repositories/  ← acceso a datos
├── templates/     ← Jinja2 (HTML)
└── static/        ← CSS, JS
```

> "Flask está organizado en **blueprints**: rutas de autenticación, vistas, sensores, SQL y Mongo. Cada blueprint llama a un servicio, y el servicio llama a un repositorio. Las rutas nunca tocan la BD directamente."

> "Esto nos permite **testear cada capa por separado** y cambiar el motor de BD sin tocar las rutas."

---

## 3.2 Demo en vivo (4 min)

### Paso 1 — Login
> "Empezamos en `/login`. La autenticación va contra MongoDB — el usuario se busca en la colección `usuarios`."

### Paso 2 — Dashboard
> "Ya dentro, vemos el dashboard con KPIs en tiempo real: temperatura, humedad, presión y luz. Esta data viene de MongoDB vía `GET /api/datos`. Se refresca cada 5 segundos."

Abrir DevTools → pestaña Network → mostrar la petición.

### Paso 3 — Simulador de Arduino ⭐
> "Como no podemos traer el Arduino a la presentación, implementamos un simulador. Elegimos **5 lecturas**, pulsamos 'Simular Arduino'…"

Pulsar el botón → mostrar el toast verde.

> "Ese toast nos dice que **5 lecturas se guardaron en MongoDB y 5 en SQL Server**. La tabla se acaba de refrescar con los nuevos datos."

> "Internamente esto es un `POST /api/simular` que ejecuta el mismo flujo que el Arduino físico: genera datos, los inserta en ambas BDs de forma independiente, y si una falla la otra se intenta igual."

### Paso 4 — Análisis (la prueba de integración)
> "Vamos a `/analisis`. Aquí están las tres operaciones SQL avanzadas y una de MongoDB en una sola pantalla."

**a) Resumen por Zona** → pulsar *"Cargar Resumen"*
> "Esto ejecuta la **vista** `vista_resumen_por_zona`. Vemos los promedios por zona y dispositivo."

**b) Clasificar Humedad** → ingresar `55` → *Clasificar*
> "Esto llama a la **función escalar**. Devuelve 'OPTIMA' porque 55% está entre 40 y 70."

Probar también con `35` → SECA, y `80` → EXCESO.

**c) Lecturas por Zona** → seleccionar Zona 1 → *Buscar*
> "Esto ejecuta el **procedimiento almacenado** `sp_lecturas_por_zona`. Las 10 lecturas más recientes con JOIN de 3 tablas, ya ordenadas."

**d) Log de Alertas** (desplazarse abajo)
> "Y aquí, en la misma pantalla, vienen las alertas de **MongoDB**. Cada documento tiene contexto rico: zona, variable, valor medido, nivel."

### Paso 5 — Gráficos
> "Y por último, `/graficos` muestra cada sensor en su propio chart con Chart.js. Click en uno, vemos el detalle."

---

## 3.3 Cierre conjunto (30 segundos · todos)

**Estudiante C** cierra:
> "En resumen, este sistema demuestra que **cada motor de base de datos hace lo que mejor sabe hacer**: SQL Server estructura y analiza, MongoDB ingiere y configura. La aplicación Flask los integra sin duplicar trabajo. Estamos abiertos a preguntas."

---

# 💬 PARTE 4 — Preguntas y respuestas (5 minutos)

## Asignación de preguntas

| Pregunta | Responde | Tema |
|----------|:--------:|------|
| P1 — ¿Por qué dos motores? | A | Arquitectura |
| P2 — Vista y JOIN | B | SQL Server |
| P3 — Procedimiento y seguridad | B | SQL Server |
| P4 — ¿Cómo testean sin Arduino? | C | Frontend/Demo |
| P5 — Patrón Repository | C | Arquitectura del código |
| P6 — Esquema flexible MongoDB | A | MongoDB |

> Si surge una pregunta nueva, el que se sienta más seguro responde y los otros complementan.

---

## P1 — ¿Por qué usar dos motores de base de datos en lugar de solo uno?

**Responde: Estudiante A**

> Cada motor resuelve un problema diferente de forma óptima.
> SQL Server provee **integridad referencial** mediante FK: si intentamos insertar una lectura con un `id_dispositivo` inexistente, SQL la rechaza. Y permite **consultas analíticas** complejas: GROUP BY sobre millones de registros, JOINs entre 3 o 4 tablas, procedimientos almacenados.
> MongoDB provee **flexibilidad de esquema**: un Arduino nuevo puede tener parámetros de calibración diferentes y simplemente agregamos ese campo al documento. También es ideal para el **log de eventos** donde cada alerta tiene contexto distinto.
> Usar ambos no duplica trabajo — los datos relacionales analíticos van a SQL, las configuraciones y eventos van a MongoDB.

---

## P2 — ¿Cómo funciona la vista `vista_resumen_por_zona` y cómo la consume Python?

**Responde: Estudiante B**

> Una vista es una consulta pre-definida almacenada con nombre. La nuestra hace JOIN entre `lecturas`, `zonas_riego` y `dispositivos`, agrupa por zona y dispositivo, y calcula promedios de temperatura, humedad, presión y luz con `AVG()`, más `COUNT(*)` para el total.
> Desde Python con pyodbc se consulta **exactamente como una tabla**:
> ```python
> cursor.execute("SELECT * FROM dbo.vista_resumen_por_zona")
> ```
> `cursor.description` nos da los nombres de columna; combinándolo con `zip()` cada fila se convierte en un diccionario que serializamos a JSON para Flask. SQL Server ejecuta el JOIN internamente — Python solo ve el resultado.

---

## P3 — ¿Cómo se ejecuta el procedimiento almacenado y por qué es seguro?

**Responde: Estudiante B**

> Con pyodbc se ejecuta así:
> ```python
> cursor.execute("EXEC dbo.sp_lecturas_por_zona ?", (id_zona,))
> ```
> Dos cosas importantes:
> 1. **Parámetro vinculado (`?`):** el valor de `id_zona` **nunca se concatena** en el string SQL. pyodbc envía el SQL y el valor por separado al driver. Si alguien envía `"1; DROP TABLE lecturas"`, ese valor se trata como un entero inválido, no como código SQL adicional. Esto hace imposible la inyección SQL.
> 2. **Lógica encapsulada:** la consulta vive en la base de datos. Si necesitamos cambiar cómo se obtienen las lecturas (agregar un filtro, cambiar el orden), modificamos el SP sin redeployar la app.

---

## P4 — ¿Cómo prueban el sistema sin tener el Arduino físico?

**Responde: Estudiante C**

> Creamos un simulador con dos formas de invocarlo. El primero es `simular_arduino.py`, un script Python que genera lecturas aleatorias dentro de rangos realistas y las inserta en ambas BDs ejecutando exactamente el mismo flujo que `guardar_datos.py` usaría con el Arduino real.
> El segundo es un **botón "Simular Arduino"** en el dashboard. El usuario elige cuántas lecturas quiere (1, 3, 5 o 10) y pulsa el botón. Esto hace un `POST /api/simular` que genera los datos en el servidor y los guarda en MongoDB y SQL Server. Si una BD falla, la otra se intenta igual y el toast muestra cuántas se guardaron en cada una.
> Esto nos permitió **validar el pipeline completo** durante el desarrollo sin depender del hardware, y demostrarlo en esta presentación.

---

## P5 — ¿Por qué organizar el código en `routes/`, `services/` y `repositories/`?

**Responde: Estudiante C**

> Es el patrón **Repository + Service**. Cada capa tiene una responsabilidad única:
> - **`routes/`** sabe sobre HTTP (decoradores Flask, status codes, JSON)
> - **`services/`** sabe sobre lógica de negocio (validar, orquestar)
> - **`repositories/`** sabe sobre la base de datos (queries, parseo de filas)
>
> La ventaja es que si mañana cambiamos MongoDB por PostgreSQL para alguna colección, **solo reescribimos su repositorio** — la ruta y el servicio no se enteran. También facilita el testing: podemos probar el servicio con un repositorio mock sin necesidad de BD real.

---

## P6 — ¿Qué significa que MongoDB tenga "esquema flexible" y por qué importa aquí?

**Responde: Estudiante A**

> SQL exige que todas las filas de una tabla tengan las mismas columnas. Si quiero agregar un campo, tengo que ejecutar `ALTER TABLE` y migrar.
> MongoDB no impone un esquema: cada documento de una colección puede tener campos diferentes. En nuestro proyecto esto importa en dos lugares:
> 1. **`configuraciones`** — cada dispositivo puede tener parámetros distintos (horarios, alertas, metadata de firmware). Modelar esto en SQL requeriría 3–4 tablas adicionales con sus FKs.
> 2. **`alertas`** — una alerta de temperatura tiene campos distintos a una de humedad. En MongoDB convive todo sin forzar un esquema rígido.
>
> No es que MongoDB sea "mejor" — es **mejor para estos casos específicos**.

---

# 📋 Checklist pre-presentación (todos)

Antes de subir a presentar verificar:

- [ ] Laptop con la app corriendo (`python app.py`) y sin errores
- [ ] Navegador con dos pestañas: `/login` y `/analisis`
- [ ] Usuario de prueba creado con credenciales conocidas
- [ ] MongoDB poblado (`python poblar_mongo.py` ya ejecutado)
- [ ] SQL Server con datos (script ya ejecutado, vista/función/SP creadas)
- [ ] Conexión a internet (MongoDB Atlas es remoto)
- [ ] Diapositivas o esta misma documentación abierta en otra pantalla
- [ ] Cada estudiante sabe **su parte + 2 preguntas** mínimo

---

# ⏱️ Plan de tiempos

| Tiempo | Estudiante | Actividad |
|:------:|:----------:|-----------|
| 0:00 — 0:30 | Todos | Apertura |
| 0:30 — 5:30 | A | Arquitectura + MongoDB |
| 5:30 — 10:30 | B | SQL Server (vista, función, SP) |
| 10:30 — 15:00 | C | Flask + Demo en vivo |
| 15:00 — 15:30 | C | Cierre |
| 15:30 — 20:00 | Todos | Preguntas |

> Si vas atrasado: salta el detalle de DevTools en la demo. Si vas adelantado: muestra el toast amarillo provocando un fallo (apaga la red para que MongoDB falle).
