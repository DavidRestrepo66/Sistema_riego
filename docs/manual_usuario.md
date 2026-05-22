# Manual de Usuario

Esta guía explica cómo usar la aplicación web una vez está instalada (ver [instalacion.md](instalacion.md) si aún no la tienes corriendo).

---

## 1. Acceso a la aplicación

Abre tu navegador en `http://localhost:5000`. Serás redirigido a la pantalla de **Login**.

### 1.1 Registro
Si es tu primera vez, haz clic en *"Crear cuenta"* y rellena:
- **Nombre completo**
- **Correo electrónico** — se usará como identificador único
- **Contraseña** — se guarda hasheada con bcrypt (nunca en texto plano)

Tras el registro, el usuario queda en la colección `usuarios` de MongoDB Atlas y se te redirige al login.

### 1.2 Inicio de sesión
Introduce correo y contraseña. La cookie de sesión se mantiene activa hasta que cierras el navegador o pulsas *"Cerrar sesión"*.

---

## 2. Dashboard (`/dashboard`)

Pantalla principal. Se refresca automáticamente cada 5 segundos.

### Componentes:

#### a) KPIs en la cabecera
Cuatro tarjetas con el valor más reciente:
- **Temperatura** (°C) — sensor DHT22
- **Humedad** (%)
- **Presión** (hPa) — sensor BMP280
- **Luz** (lux) — sensor LDR

Cada tarjeta muestra el delta vs. la lectura anterior (↑/↓ con la diferencia).

#### b) Botones de acción
- **Refrescar** — fuerza una recarga inmediata de datos
- **Selector de cantidad** — 1, 3, 5 o 10 lecturas (para el simulador)
- **Simular Arduino** — inserta lecturas falsas en ambas bases de datos (sin Arduino físico)
- **Ver gráficos** — navega a `/graficos`

#### c) Tendencia de humedad
Gráfico de línea con las últimas lecturas de humedad. Se actualiza junto con los KPIs.

#### d) Alertas recientes
Últimos 5 eventos críticos de la colección `alertas` de MongoDB.

#### e) Tabla de lecturas recientes
Últimas 20 lecturas con todas las variables. Stream desde MongoDB.

---

## 3. Cómo simular lecturas sin Arduino

Esta es la forma más rápida de **comprobar que ambas bases de datos funcionan**.

### Procedimiento:

1. Estando en `/dashboard`, elige cuántas lecturas quieres en el selector (1, 3, 5 o 10)
2. Pulsa el botón **"Simular Arduino"**
3. El botón cambia a *"Simulando…"* mientras se ejecuta
4. Aparece un **toast** en la esquina inferior derecha:
   - **Verde** ✅ — ambas BDs guardaron correctamente
   - **Amarillo** ⚠ — una falló (revisar mensaje de error)
   - **Rojo** ✖ — ambas fallaron
5. El KPI y la tabla se refrescan automáticamente con los nuevos datos

### Qué hace internamente:

```
Botón → POST /api/simular {n}
  → Genera N lecturas con random.uniform
  → INSERT INTO lecturas (SQL Server)
  → insert_one (MongoDB Atlas)
  → Respuesta {mongo: {ok}, sql: {ok}}
```

Es **el mismo flujo** que ejecutaría `guardar_datos.py` con el Arduino real, solo que con datos generados.

### Detalle de los datos generados:

| Variable | Rango |
|----------|-------|
| `temp_dht` | 18.0 – 35.0 °C |
| `humedad` | 30.0 – 80.0 % |
| `temp_bmp` | `temp_dht` ± 0.5 °C |
| `presion` | 1005.0 – 1025.0 hPa |
| `luz` | 100.0 – 1000.0 lux |
| `id_dispositivo` | 1 (Arduino-01) |
| `id_zona` | 1 (Zona A Tomate) |
| `fecha` | `datetime.now()` |

---

## 4. Página de Análisis (`/analisis`)

Esta página es la **prueba de integración** SQL Server + MongoDB.

### 4.1 Resumen por Zona
Botón *"Cargar Resumen"* → ejecuta `vista_resumen_por_zona` en SQL Server.

Muestra una tabla con:
- Zona
- Dispositivo
- Total de lecturas
- Promedio de temperatura, humedad, presión y luz

Internamente: `JOIN` de 3 tablas + `GROUP BY` + agregaciones `AVG/COUNT`.

### 4.2 Clasificar Humedad
1. Ingresa un valor numérico (ej. `35`, `55`, `80`)
2. Pulsa *"Clasificar"*
3. SQL Server ejecuta la función `dbo.fn_clasificar_humedad(?)`
4. Se muestra el resultado: **SECA**, **OPTIMA** o **EXCESO**

### 4.3 Lecturas por Zona
1. Selecciona una zona (1, 2 o 3)
2. Pulsa *"Buscar"*
3. SQL Server ejecuta `EXEC dbo.sp_lecturas_por_zona <id>`
4. Se muestran las **10 lecturas más recientes** de esa zona

### 4.4 Log de Alertas
Lista de eventos guardados en la colección `alertas` de MongoDB. Cada alerta indica:
- Fecha
- Zona afectada
- Variable que disparó la alerta
- Valor medido vs. umbral
- Nivel de criticidad (normal / advertencia / crítico)

---

## 5. Página de Gráficos (`/graficos`)

Muestra los gráficos de las 5 variables (temperatura DHT, temperatura BMP, humedad, presión, luz).

Al hacer clic en uno → `/graficos/<tipo>` → vista de detalle con un gráfico más grande.

Los datos se consultan a MongoDB vía `/api/datos`.

---

## 6. Tema claro / oscuro

En la cabecera, ícono de sol/luna → alterna entre modo claro y oscuro.
La preferencia se guarda en `localStorage` del navegador.

---

## 7. Resumen de pantallas

| Ruta | ¿Qué hace? | Origen de datos |
|------|-----------|-----------------|
| `/login` · `/registro` | Autenticación | MongoDB (`usuarios`) |
| `/dashboard` | Tiempo real + KPIs + simulador | MongoDB (`lecturas`, `alertas`) |
| `/analisis` | Vista, función, SP + alertas | SQL Server + MongoDB |
| `/graficos` | Charts de cada sensor | MongoDB (`lecturas`) |
| `/graficos/<tipo>` | Detalle de un sensor | MongoDB (`lecturas`) |

---

## 8. Flujo recomendado para una prueba completa

1. **Login** → `/dashboard`
2. Pulsar **"Simular Arduino"** con `5 lecturas` → ver toast verde
3. Verificar que la **tabla de lecturas** se actualiza
4. Ir a `/analisis`
5. Pulsar **"Cargar Resumen"** → ver promedios por zona
6. Clasificar humedad **35** (debe decir SECA), **55** (OPTIMA), **80** (EXCESO)
7. Buscar lecturas de la **Zona 1** → ver 10 más recientes
8. Ir a `/graficos` → revisar los 5 gráficos
9. Hacer clic en uno → ver el detalle

Si todos estos pasos funcionan, **el sistema completo está operativo**.
