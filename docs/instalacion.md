# Guía de Instalación

Pasos detallados para tener el sistema corriendo desde cero. Tiempo estimado: **20–30 minutos** la primera vez.

---

## 1. Requisitos previos

| Herramienta | Versión | Notas |
|-------------|---------|-------|
| Python | 3.9 o superior | `python --version` |
| SQL Server | 2019+ (Express sirve) | Local o remoto |
| SQL Server Management Studio (SSMS) | última versión | Solo Windows |
| ODBC Driver for SQL Server | 17 | [descarga oficial Microsoft](https://learn.microsoft.com/sql/connect/odbc/) |
| Cuenta MongoDB Atlas | gratuita (M0) | https://www.mongodb.com/cloud/atlas |
| Git | cualquiera | Para clonar el repo |

---

## 2. Instalación paso a paso

### Paso 1 — Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd aa
```

### Paso 2 — Instalar dependencias Python

Se recomienda usar entorno virtual:

```bash
python -m venv venv
# Linux / macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

pip install flask pymongo pyodbc python-dotenv bcrypt pyserial
```

### Paso 3 — Configurar MongoDB Atlas

1. Inicia sesión en [MongoDB Atlas](https://cloud.mongodb.com)
2. Crea un cluster gratuito (M0) si no tienes uno
3. **Database Access** → crea un usuario con rol *Read and write to any database*
4. **Network Access** → añade tu IP actual (o `0.0.0.0/0` para desarrollo, no recomendado en producción)
5. **Connect** → *Drivers* → copia la cadena de conexión que se parece a:
   ```
   mongodb+srv://USUARIO:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
   ```

### Paso 4 — Configurar SQL Server

1. Abre **SQL Server Management Studio (SSMS)** y conéctate a tu instancia
2. Anota el "Server name" exacto (ej. `DESKTOP-ABC123\SQLEXPRESS`)
3. Abre el archivo `schema_sensores.sql` y ejecútalo completo con **F5**
4. Verifica que se creó la base `sensores` con 4 tablas, 1 vista, 1 función y 1 procedimiento

```sql
-- Comprobación rápida
USE sensores;
SELECT COUNT(*) AS dispositivos FROM dispositivos;  -- esperado: 3
SELECT COUNT(*) AS zonas         FROM zonas_riego;   -- esperado: 3
SELECT COUNT(*) AS lecturas      FROM lecturas;      -- esperado: 18
SELECT * FROM dbo.vista_resumen_por_zona;            -- debe retornar filas
```

### Paso 5 — Crear el archivo `.env`

En la raíz del proyecto (mismo nivel que `README.md`), crea un archivo `.env`:

```env
# Flask
SECRET_KEY=cambia-esto-por-una-clave-larga-y-aleatoria

# MongoDB
MONGO_URI=mongodb+srv://USUARIO:PASSWORD@cluster0.xxxxx.mongodb.net/?appName=Cluster0
DATABASE_NAME=sensores_mongo

# Arduino (solo necesario si usas el Arduino físico)
ARDUINO_PORT=COM3
BAUD_RATE=9600

# SQL Server
SQL_SERVER=DESKTOP-ABC123\SQLEXPRESS
SQL_DATABASE=sensores
SQL_USER=sa
SQL_PASSWORD=tu_password
```

> **Importante:** el archivo `.env` está en `.gitignore`. Nunca lo subas al repositorio.

### Paso 6 — Poblar MongoDB

```bash
python poblar_mongo.py
```

Salida esperada:
```
Configuraciones insertadas: 3 documentos
Alertas insertadas: 14 documentos
Poblado de MongoDB completado exitosamente.
```

### Paso 7 — Probar conexiones

```bash
cd SensoresWeb_MongoDB
python test_sql.py
# Esperado: "SQL Server conectado correctamente"
```

Para MongoDB, lo más rápido es ejecutar Flask y verificar que arranca sin errores.

### Paso 8 — Levantar la aplicación Flask

```bash
# Desde SensoresWeb_MongoDB/
python app.py
```

Salida esperada:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

Abre el navegador en `http://localhost:5000` → deberías ver la pantalla de login.

### Paso 9 — Crear un usuario

1. Ir a `http://localhost:5000/registro`
2. Completar nombre, correo y contraseña
3. Iniciar sesión

### Paso 10 — Generar lecturas de prueba

Sin Arduino conectado, usa el simulador desde el dashboard:

1. Una vez en `/dashboard`, elige cantidad en el selector
2. Pulsa **"Simular Arduino"**
3. Verifica el toast de éxito y que la tabla se refresca

---

## 3. Verificación final

Una instalación correcta debe permitir:

- [ ] Login y registro funcionan
- [ ] `/dashboard` muestra la tabla y los KPIs
- [ ] El botón "Simular Arduino" inserta lecturas en ambas BDs
- [ ] `/analisis` carga el resumen por zona (SQL Server)
- [ ] `/analisis` muestra alertas (MongoDB)
- [ ] `/graficos` renderiza los charts con datos

---

## 4. Problemas comunes

### Error `pyodbc.Error: ('IM002', ...)`
**Causa:** ODBC Driver 17 no está instalado.
**Solución:** Descarga e instala desde [aquí](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server).

### Error `Login failed for user 'sa'`
**Causa:** SQL Server no acepta autenticación SQL o la contraseña es incorrecta.
**Solución:** En SSMS → click derecho en el servidor → *Properties* → *Security* → activar *SQL Server and Windows Authentication mode* → reiniciar el servicio SQL Server.

### Error `[HY000] [Microsoft][SQL Server Native Client] No connection could be made`
**Causa:** El nombre del servidor en `.env` no coincide con la instancia real.
**Solución:** Abre SSMS, copia el nombre exacto del "Server name" y pégalo en `SQL_SERVER` del `.env`. Usa `\\` o cadena raw si tiene barra invertida.

### Error MongoDB `ServerSelectionTimeoutError`
**Causa:** Tu IP no está autorizada en Atlas, o la cadena de conexión es incorrecta.
**Solución:**
1. Atlas → Network Access → añade tu IP
2. Verifica que `USUARIO:PASSWORD` en la URI son correctos
3. Si la password tiene caracteres especiales (`@`, `:`, `/`), debe estar URL-encoded

### Error `ModuleNotFoundError: No module named 'flask'`
**Causa:** El entorno virtual no está activado o las dependencias no se instalaron.
**Solución:**
```bash
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install flask pymongo pyodbc python-dotenv bcrypt pyserial
```

### El botón "Simular Arduino" responde con error SQL
**Causa:** No existe el `id_dispositivo=1` o `id_zona=1` en SQL Server.
**Solución:** Ejecuta `schema_sensores.sql` completo en SSMS (incluye los `INSERT` de datos de prueba).

### El botón "Simular Arduino" responde con error MongoDB
**Causa:** La cadena de conexión MongoDB es inválida o no hay conectividad.
**Solución:** Verifica `MONGO_URI` en `.env` y tu acceso a internet. Prueba la conexión con MongoDB Compass usando la misma URI.

### `python poblar_mongo.py` falla
**Causa:** El `.env` no se está cargando o `MONGO_URI` está vacío.
**Solución:** El script importa `Config` que carga `.env` desde la raíz. Ejecuta el comando desde la raíz del proyecto, no desde subcarpetas.

---

## 5. Próximos pasos

Una vez funcionando:
- Lee el [manual de usuario](manual_usuario.md) para conocer cada pantalla
- Revisa la [referencia de API](api.md) si vas a integrar con otro sistema
- Si vas a presentar el proyecto, consulta el [guion de presentación](presentacion_guion.md)
