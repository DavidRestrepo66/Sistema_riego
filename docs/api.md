# Referencia de la API REST

Todos los endpoints viven en `http://localhost:5000` durante desarrollo. Las rutas que devuelven JSON están bajo `/api/*`.

## Convenciones

- **Formato:** JSON en `Content-Type: application/json`
- **Autenticación:** sesión Flask vía cookie (login en `/login`). Los endpoints marcados con 🔒 requieren sesión activa.
- **Errores:** se devuelve un JSON con `{"error": "mensaje"}` y código HTTP apropiado.

---

## 1. Autenticación (HTML)

### `GET /login`
Renderiza el formulario de login.

### `POST /login`
Inicia sesión.

| Campo | Tipo | Origen | Requerido |
|-------|------|--------|-----------|
| `email` | string | form-data | sí |
| `password` | string | form-data | sí |

**Respuesta:** redirect a `/dashboard` (éxito) o a `/login` con flash (fallo).

### `GET /registro`
Renderiza el formulario de registro.

### `POST /registro`
Crea un nuevo usuario.

| Campo | Tipo | Origen | Requerido |
|-------|------|--------|-----------|
| `nombre` | string | form-data | sí |
| `email` | string | form-data | sí |
| `password` | string | form-data | sí |

**Respuesta:** redirect a `/login` con mensaje flash.

### `GET /logout`
Cierra la sesión y redirige a `/login`.

---

## 2. Vistas HTML 🔒

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/dashboard` | Tabla en vivo, KPIs, botón simulador |
| `/analisis` | Vistas SQL Server + alertas MongoDB |
| `/graficos` | Gráficos por tipo de sensor |
| `/graficos/<tipo>` | Detalle de un sensor específico |

`<tipo>` ∈ `{temp_dht, temp_bmp, humedad, presion, luz}`.

---

## 3. API · Lecturas de sensores

### `GET /api/datos`
Devuelve las lecturas guardadas en MongoDB (colección `lecturas`), ordenadas por fecha descendente.

**Respuesta** `200 OK`:
```json
[
  {
    "id": "664f...e3",
    "fecha": "2026-05-22 14:30:00",
    "temp_dht": 24.5,
    "humedad": 62.3,
    "temp_bmp": 24.2,
    "presion": 1013.5,
    "luz": 750.0
  }
]
```

### `POST /api/simular` 🔒
Genera y guarda lecturas simuladas en MongoDB **y** SQL Server.

**Body** `application/json`:
```json
{
  "n": 5
}
```
- `n` (opcional, default `1`, máximo `10`): número de lecturas a generar.

**Respuesta** `200 OK`:
```json
{
  "n": 5,
  "mongo": { "ok": 5, "error": null },
  "sql":   { "ok": 5, "error": null }
}
```

En caso de fallo parcial, `ok` indica cuántas se guardaron y `error` contiene el mensaje:

```json
{
  "n": 3,
  "mongo": { "ok": 3, "error": null },
  "sql":   { "ok": 0, "error": "Login failed for user 'sa'" }
}
```

**Ejemplo con `curl`:**
```bash
curl -X POST http://localhost:5000/api/simular \
  -H "Content-Type: application/json" \
  -b "session=COOKIE_DE_SESION" \
  -d '{"n": 3}'
```

---

## 4. API · SQL Server 🔒

Todas devuelven JSON. Prefijo: `/api/sql`.

### `GET /api/sql/resumen`
Ejecuta `SELECT * FROM dbo.vista_resumen_por_zona`.

**Respuesta** `200 OK`:
```json
[
  {
    "zona": "Zona A",
    "dispositivo": "Arduino-01",
    "total_lecturas": 6,
    "prom_temp": 24.17,
    "prom_humedad": 61.75,
    "prom_presion": 1012.95,
    "prom_luz": 586.75
  }
]
```

### `GET /api/sql/zona/<int:id_zona>`
Ejecuta `EXEC dbo.sp_lecturas_por_zona ?` con el id proporcionado.

**Parámetro de ruta:**
- `id_zona`: entero (1, 2 o 3 según los datos de prueba)

**Respuesta** `200 OK`:
```json
[
  {
    "id_lectura": 17,
    "zona": "Zona C",
    "dispositivo": "Arduino-03",
    "fecha": "2024-04-02 18:00:00",
    "temp_dht": 27.1,
    "humedad": 43.9,
    "temp_bmp": 26.8,
    "presion": 1012.1,
    "luz": 810.0
  }
]
```

### `GET /api/sql/humedad/<float:valor>`
Ejecuta `SELECT dbo.fn_clasificar_humedad(?)`.

**Parámetro de ruta:**
- `valor`: número decimal (ej. `55.5`)

**Respuesta** `200 OK`:
```json
{
  "valor": 55.5,
  "clasificacion": "OPTIMA"
}
```

Valores posibles de `clasificacion`: `SECA` (<40), `OPTIMA` (40–70), `EXCESO` (>70).

---

## 5. API · MongoDB 🔒

Prefijo: `/api/mongo`.

### `GET /api/mongo/alertas`
Devuelve documentos de la colección `alertas` ordenados por fecha descendente.

**Respuesta** `200 OK`:
```json
[
  {
    "_id": "...",
    "fecha": "2026-05-22T13:00:00Z",
    "id_zona": 1,
    "zona": "Zona A Tomate",
    "variable": "humedad",
    "valor_medido": 18.5,
    "umbral_superado": 30.0,
    "nivel": "critico",
    "mensaje": "Humedad muy por debajo del mínimo crítico"
  }
]
```

### `GET /api/mongo/configuraciones`
Devuelve documentos de la colección `configuraciones`, una por dispositivo.

**Respuesta** `200 OK`:
```json
[
  {
    "_id": "...",
    "id_dispositivo": 1,
    "nombre": "Arduino Norte",
    "horario_riego": {
      "inicio": "06:00",
      "fin": "07:30",
      "dias": ["lunes", "miercoles", "viernes"]
    },
    "alertas_activas": ["humedad", "temp_dht"],
    "umbral_bateria": 20,
    "metadata": {
      "firmware": "v2.1",
      "ultima_calibracion": "2024-11-15"
    }
  }
]
```

---

## 6. Códigos de error

| Código | Significado | Causa típica |
|--------|-------------|--------------|
| `302` | Redirect | Sesión no válida → se redirige a `/login` |
| `400` | Bad Request | Parámetro inválido (ej. `tipo` desconocido en `/graficos/<tipo>`) |
| `500` | Internal Server Error | Falla de conexión a BD, error SQL, etc. El JSON incluye `error` con el mensaje. |

---

## 7. Resumen de endpoints

| # | Método | Endpoint | Auth | Devuelve |
|---|--------|----------|:----:|----------|
| 1 | GET   | `/` | — | redirect `/login` |
| 2 | GET/POST | `/login` | — | HTML |
| 3 | GET/POST | `/registro` | — | HTML |
| 4 | GET   | `/logout` | — | redirect |
| 5 | GET   | `/dashboard` | 🔒 | HTML |
| 6 | GET   | `/analisis` | 🔒 | HTML |
| 7 | GET   | `/graficos` | 🔒 | HTML |
| 8 | GET   | `/graficos/<tipo>` | 🔒 | HTML |
| 9 | GET   | `/api/datos` | — | JSON |
| 10 | POST | `/api/simular` | 🔒 | JSON |
| 11 | GET  | `/api/sql/resumen` | 🔒 | JSON |
| 12 | GET  | `/api/sql/zona/<id>` | 🔒 | JSON |
| 13 | GET  | `/api/sql/humedad/<valor>` | 🔒 | JSON |
| 14 | GET  | `/api/mongo/alertas` | 🔒 | JSON |
| 15 | GET  | `/api/mongo/configuraciones` | 🔒 | JSON |
