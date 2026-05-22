# Guion de Presentación — Sistema de Monitoreo de Sensores con SQL Server + MongoDB

---

## 1. Arquitectura del Sistema

```
┌─────────────┐
│   Arduino   │  (sensores DHT, BMP, LDR)
└──────┬──────┘
       │ Serial (USB)
       ▼
┌─────────────────────┐
│  guardar_datos.py   │  (script Python standalone)
└──────┬──────────────┘
       │                      escribe lecturas crudas
       ├──────────────────────────────────────────────► MongoDB Atlas
       │                                                 └── colección: lecturas (buffer)
       │
       │  inserta lecturas procesadas
       ▼
┌──────────────────────────────┐
│       SQL Server             │
│  ┌─────────────────────────┐ │
│  │ tabla: dispositivos     │ │
│  │ tabla: zonas_riego      │ │
│  │ tabla: lecturas         │ │
│  │ tabla: umbrales_alerta  │ │
│  │ vista: vista_resumen... │ │
│  │ función: fn_clasif...   │ │
│  │ SP: sp_lecturas_zona    │ │
│  └─────────────────────────┘ │
└──────────────┬───────────────┘
               │
               │  consultas SQL (pyodbc)
               ▼
┌──────────────────────────────────────────────┐
│           Flask Application                  │
│  routes/  services/  repositories/           │
│                                              │
│  ◄── SQL Server: vista, función, SP          │
│  ◄── MongoDB Atlas: alertas, configs, users  │
└──────────────────────┬───────────────────────┘
                       │  HTTP (Jinja2 + AJAX)
                       ▼
              ┌─────────────┐
              │   Browser   │
              │  Dashboard  │
              │  /analisis  │
              └─────────────┘
```

**Resumen de capas:**
- **Capa de adquisición:** Arduino → `guardar_datos.py` → doble escritura (SQL Server + MongoDB)
- **Capa de datos relacionales:** SQL Server con integridad referencial, vistas, funciones y procedimientos
- **Capa de datos documentales:** MongoDB Atlas para ingesta en tiempo real, configuraciones y log de alertas
- **Capa de aplicación:** Flask con repositorios separados por motor de base de datos
- **Capa de presentación:** Browser con Jinja2 templates y llamadas AJAX a la API REST

---

## 2. Modelo Relacional SQL Server

| Tabla | Columnas Principales | Tipo de Relación |
|-------|---------------------|-----------------|
| **dispositivos** | `id` (PK), `nombre`, `ubicacion`, `tipo`, `fecha_instalacion` | Tabla maestra de dispositivos Arduino. Sin FK entrantes — es referenciada por `lecturas` y `umbrales_alerta`. |
| **zonas_riego** | `id` (PK), `nombre`, `tipo_cultivo`, `descripcion` | Tabla maestra de zonas de cultivo. Referenciada por `lecturas` y `umbrales_alerta`. |
| **lecturas** | `id` (PK), `id_dispositivo` (FK → dispositivos), `id_zona` (FK → zonas_riego), `fecha`, `temp_dht`, `humedad`, `temp_bmp`, `presion`, `luz` | Tabla central de hechos. Muchos-a-uno con `dispositivos` y `zonas_riego`. Una lectura pertenece a un dispositivo en una zona. |
| **umbrales_alerta** | `id` (PK), `id_zona` (FK → zonas_riego), `variable`, `valor_min`, `valor_max`, `activo` | Configuración de alertas por zona y variable. Muchos-a-uno con `zonas_riego`. Permite múltiples umbrales por zona. |

**Diagrama de relaciones:**
```
dispositivos ──┐
               ├──► lecturas ◄── zonas_riego ──► umbrales_alerta
```

---

## 3. Elementos Avanzados SQL Server

### Vista: `vista_resumen_por_zona`

Consulta pre-definida que combina tres tablas mediante JOINs y agrupa los resultados por zona y dispositivo.

**Funcionamiento interno:**
- `JOIN` entre `lecturas`, `zonas_riego` y `dispositivos`
- `GROUP BY` por zona y dispositivo
- Funciones de agregación: `AVG()` para temperatura (DHT y BMP), humedad, presión y luz
- `COUNT(*)` para el total de lecturas por grupo

**Desde Python:**
```python
cursor.execute("SELECT * FROM dbo.vista_resumen_por_zona")
columns = [col[0] for col in cursor.description]
rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
```
Se consulta igual que una tabla ordinaria — SQL Server ejecuta el JOIN internamente de forma transparente.

---

### Función Escalar: `fn_clasificar_humedad(valor)`

Función que recibe un valor numérico de humedad y retorna una clasificación textual.

**Lógica de clasificación:**
- `< 40%` → `'SECA'`
- `40% – 70%` → `'OPTIMA'`
- `> 70%` → `'EXCESO'`

**Desde Python:**
```python
cursor.execute("SELECT dbo.fn_clasificar_humedad(?)", (valor,))
resultado = cursor.fetchone()[0]  # retorna 'SECA', 'OPTIMA' o 'EXCESO'
```
El `?` es un parámetro vinculado gestionado por pyodbc — nunca se concatena directamente en el string SQL.

---

### Procedimiento Almacenado: `sp_lecturas_por_zona(@id_zona INT)`

Procedimiento parametrizado que retorna las últimas 10 lecturas de una zona específica.

**Funcionamiento interno:**
- Recibe `@id_zona` como parámetro entero
- `JOIN` entre `lecturas`, `dispositivos` y `zonas_riego`
- Filtro `WHERE lecturas.id_zona = @id_zona`
- `ORDER BY fecha DESC` + `TOP 10` para obtener las más recientes

**Desde Python:**
```python
cursor.execute("EXEC dbo.sp_lecturas_por_zona ?", (id_zona,))
columns = [col[0] for col in cursor.description]
rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
```
El uso de `?` como parámetro vinculado previene inyección SQL — nunca se construye el string con f-strings o concatenación.

---

## 4. Colecciones MongoDB (rol complementario)

MongoDB Atlas actúa como complemento a SQL Server, no como duplicado. Cada colección tiene un rol diferenciado:

### `usuarios`
**Rol:** Autenticación flexible.
El esquema de un usuario puede variar sin necesidad de ejecutar `ALTER TABLE`. Un usuario básico tiene `username` y `password_hash`; en el futuro puede agregar `roles`, `preferencias`, `último_acceso` sin romper la colección ni requerir migraciones. Flask-Login se integra directamente consultando esta colección.

### `lecturas`
**Rol:** Buffer de ingesta en tiempo real.
`guardar_datos.py` escribe cada lectura del Arduino primero en MongoDB como documento crudo. Esto garantiza que ningún dato se pierda aunque SQL Server esté temporalmente no disponible. Actúa como cola de mensajes liviana antes del procesamiento.

### `configuraciones`
**Rol:** Configuración por dispositivo con esquema variable.
Cada dispositivo Arduino puede tener horarios de riego personalizados, alertas activas, metadata de firmware, intervalo de muestreo y parámetros de calibración. Esta información cambia frecuentemente y tiene estructura diferente por dispositivo — MongoDB permite actualizar estos documentos sin alterar el esquema de ninguna tabla.

### `alertas`
**Rol:** Log de eventos con estructura variable y contexto rico.
Cada alerta registra: zona afectada, variable que superó el umbral, valor medido, nivel de criticidad (`normal`/`advertencia`/`crítico`), timestamp y contexto adicional. La estructura varía por tipo de alerta — un documento de temperatura tiene campos distintos a uno de humedad. MongoDB almacena este historial sin forzar un esquema rígido.

---

### Por qué complementan y no duplican

| Aspecto | SQL Server | MongoDB |
|---------|-----------|---------|
| Fortaleza | Integridad referencial, JOINs complejos, consultas analíticas | Esquema flexible, ingesta rápida, documentos anidados |
| Uso en este proyecto | Datos históricos estructurados, vistas y SPs para análisis | Configuraciones evolutivas, buffer de ingesta, log de eventos |
| Modelo | Relacional normalizado | Documental desnormalizado |
| Migraciones | Requieren `ALTER TABLE` | No requeridas (schema-less) |

SQL Server = modelo relacional analítico (integridad, promedios, consultas cruzadas).
MongoDB = ingesta flexible, configuración evolutiva, log de eventos con estructura variable.

---

## 5. Guion de Demo en Vivo

### Paso 1 — Abrir la aplicación
Abrir el navegador en `http://localhost:5000`. Se muestra la pantalla de **login**.
> "La autenticación está gestionada por MongoDB — el usuario se busca en la colección `usuarios` de Atlas."

### Paso 2 — Iniciar sesión
Ingresar las credenciales de demo. Flask-Login gestiona la sesión. Si las credenciales son correctas, redirige al dashboard.

### Paso 3 — Dashboard con datos de MongoDB
En el dashboard se muestra una tabla de lecturas recientes cargadas dinámicamente desde el endpoint `/api/datos`.
> "Esta tabla consume la colección `lecturas` de MongoDB Atlas. Es el buffer de ingesta en tiempo real — datos crudos del Arduino."
Inspeccionar la llamada AJAX en DevTools: `GET /api/datos` retorna JSON con los documentos de MongoDB.

### Paso 4 — Navegar a `/analisis`
Hacer clic en "Análisis" en el menú de navegación. Se abre la página de análisis avanzado con SQL Server.

### Paso 5 — Resumen por Zona (vista SQL Server)
En la sección "Resumen por Zona", hacer clic en "Cargar Resumen".
> "Esto ejecuta `SELECT * FROM dbo.vista_resumen_por_zona` — una vista de SQL Server que hace JOIN entre 3 tablas y agrupa por zona. Flask recibe el resultado y lo serializa a JSON."
Mostrar la tabla con promedios de temperatura, humedad, presión y luz por zona.

### Paso 6 — Clasificar Humedad (función escalar)
En la sección "Clasificar Humedad":
1. Ingresar `35` → click "Clasificar" → se muestra **"SECA"**
2. Borrar y ingresar `55` → click "Clasificar" → se muestra **"OPTIMA"**
> "Flask ejecuta `SELECT dbo.fn_clasificar_humedad(?)` con el valor como parámetro vinculado. SQL Server evalúa la función escalar y retorna la clasificación."

### Paso 7 — Lecturas por Zona (procedimiento almacenado)
En la sección "Lecturas por Zona":
1. Seleccionar "Zona 1" en el selector
2. Click "Buscar"
> "Esto ejecuta `EXEC dbo.sp_lecturas_por_zona ?` con el ID de zona como parámetro. El SP hace JOIN entre 3 tablas, ordena por fecha descendente y retorna TOP 10."
Mostrar la tabla con las últimas 10 lecturas de la zona seleccionada.

### Paso 8 — Log de Alertas (MongoDB)
Desplazarse a la sección "Log de Alertas" en la página de análisis.
> "Esta sección viene de MongoDB Atlas, colección `alertas`. Cada alerta tiene contexto rico: zona, variable, valor medido y nivel de criticidad. La estructura varía por tipo de alerta."
Mostrar los documentos de alerta con sus diferentes campos.

### Paso 9 — Conclusión de la demo
> "En esta única pantalla de `/analisis` hemos consumido:
> - SQL Server: una vista (JOIN + GROUP BY), una función escalar y un procedimiento almacenado
> - MongoDB Atlas: colección de alertas con esquema flexible
>
> Cada motor hace lo que mejor sabe hacer."

---

## 6. Preguntas Técnicas Probables

---

**P1: ¿Por qué usar dos motores de base de datos en lugar de solo uno?**

**R:** Cada motor resuelve un problema diferente de forma óptima.

SQL Server provee integridad referencial mediante claves foráneas — si intentamos insertar una lectura con un `id_dispositivo` inexistente, SQL Server lo rechaza. También provee consultas analíticas complejas: GROUP BY sobre millones de registros, JOINs entre 3 o 4 tablas, funciones de ventana, procedimientos almacenados con lógica encapsulada. Para los datos históricos de sensores que tienen estructura fija y necesitan ser analizados en conjunto, el modelo relacional es la herramienta correcta.

MongoDB provee flexibilidad de esquema para situaciones donde la estructura de los datos cambia: un dispositivo Arduino nuevo puede tener parámetros de calibración diferentes a los anteriores, y en MongoDB simplemente se agrega ese campo al documento sin alterar nada más. También es ideal para log de eventos donde cada alerta puede tener un contexto diferente según la variable que disparó la alerta.

Usar ambos no duplica trabajo — los datos relacionales analíticos van a SQL Server, los datos de configuración y log de eventos van a MongoDB.

---

**P2: ¿Cómo funciona la vista `vista_resumen_por_zona` y cómo la consume Python?**

**R:** Una vista en SQL Server es una consulta pre-definida almacenada con un nombre. Su definición incluye:

```sql
SELECT z.nombre AS zona, d.nombre AS dispositivo,
       AVG(l.temp_dht) AS prom_temp, AVG(l.humedad) AS prom_humedad,
       AVG(l.presion) AS prom_presion, AVG(l.luz) AS prom_luz,
       COUNT(*) AS total_lecturas
FROM lecturas l
JOIN zonas_riego z ON l.id_zona = z.id
JOIN dispositivos d ON l.id_dispositivo = d.id
GROUP BY z.nombre, d.nombre
```

Desde Python con pyodbc, se consulta exactamente igual que una tabla ordinaria:

```python
cursor.execute("SELECT * FROM dbo.vista_resumen_por_zona")
columns = [col[0] for col in cursor.description]
rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
```

`cursor.description` contiene los nombres de columnas del resultado. Combinado con `zip`, convierte cada fila en un diccionario que puede serializarse directamente a JSON para la respuesta de Flask. SQL Server ejecuta el JOIN internamente — Python solo ve el resultado final.

---

**P3: ¿Cómo se ejecuta el procedimiento almacenado desde Python y por qué es seguro?**

**R:** Con pyodbc, el procedimiento se ejecuta así:

```python
cursor.execute("EXEC dbo.sp_lecturas_por_zona ?", (id_zona,))
```

Hay dos aspectos clave en esta línea:

1. **Parámetro vinculado (`?`):** El valor de `id_zona` nunca se concatena en el string SQL. pyodbc envía el string `"EXEC dbo.sp_lecturas_por_zona ?"` y el valor `id_zona` como un parámetro separado al driver de SQL Server. El motor de base de datos recibe el parámetro ya tipado y lo trata como un valor entero, no como texto SQL. Esto hace imposible la inyección SQL — si alguien envía `"1; DROP TABLE lecturas"`, ese valor se trata como un entero inválido, no como código SQL adicional.

2. **Procedimiento almacenado:** El SP encapsula la lógica de consulta en SQL Server:
   ```sql
   SELECT TOP 10 l.*, d.nombre AS dispositivo, z.nombre AS zona
   FROM lecturas l
   JOIN dispositivos d ON l.id_dispositivo = d.id
   JOIN zonas_riego z ON l.id_zona = z.id
   WHERE l.id_zona = @id_zona
   ORDER BY l.fecha DESC
   ```
   Esta lógica vive en la base de datos, no en el código Python. Si necesitamos cambiar cómo se obtienen las lecturas (agregar un JOIN, cambiar el orden), modificamos el SP sin tocar el código de la aplicación.
