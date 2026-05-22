# Sistema de Monitoreo de Sensores IoT — Riego Agrícola

Aplicación web Flask que integra **SQL Server** y **MongoDB Atlas** para monitorear sensores Arduino en zonas de cultivo. Proyecto final de Bases de Datos 2.

---

## Arquitectura

```
Arduino (sensores)
       │
       ▼
guardar_datos.py ──► SQL Server (lecturas)
       │
       └──────────► MongoDB Atlas (lecturas)

Navegador ◄──── Flask App ──► SQL Server  (vista / SP / función)
                         └──► MongoDB Atlas (alertas / configuraciones)
```

**SQL Server** maneja el modelo relacional-analítico (4 tablas, vistas, procedimientos, funciones).  
**MongoDB Atlas** maneja ingesta flexible y configuraciones (usuarios, lecturas, alertas, configuraciones de dispositivos).

---

## Requisitos previos

| Herramienta | Versión mínima |
|---|---|
| Python | 3.9+ |
| SQL Server | 2019+ (Express sirve) |
| ODBC Driver for SQL Server | 17 |
| MongoDB Atlas | cuenta gratuita |

### Paquetes Python necesarios

```bash
pip install flask pymongo pyodbc python-dotenv bcrypt pyserial
```

---

## Estructura del proyecto

```
aa/
├── .env                          # Credenciales (NO se sube al repo)
├── .gitignore
├── schema_sensores.sql           # Script SQL Server completo
├── poblar_mongo.py               # Poblar colecciones MongoDB
├── exportar_mongo.py             # Exportar colecciones a JSON
├── guardar_datos.py              # Leer Arduino y guardar en ambas BDs
├── mongo_export/                 # JSONs exportados (generado)
├── docs/
│   └── presentacion_guion.md    # Guion para la presentación
└── SensoresWeb_MongoDB/
    ├── app.py                    # Entry point de Flask
    ├── config.py                 # Configuración desde .env
    ├── repositories/
    │   ├── sensor_repository.py  # MongoDB: lecturas
    │   ├── user_repository.py    # MongoDB: usuarios
    │   ├── sql_repository.py     # SQL Server: vista, SP, función
    │   └── mongo_extra_repository.py  # MongoDB: alertas, configuraciones
    ├── services/
    │   ├── auth_service.py
    │   ├── sensor_service.py
    │   └── sql_service.py
    ├── routes/
    │   ├── auth_routes.py        # /login /registro /logout
    │   ├── view_routes.py        # /dashboard /analisis /graficos
    │   ├── sensor_routes.py      # /api/datos
    │   ├── sql_routes.py         # /api/sql/*
    │   └── mongo_routes.py       # /api/mongo/*
    ├── templates/
    │   ├── login.html
    │   ├── registro.html
    │   ├── dashboard.html
    │   ├── analisis.html         # Página integración SQL + Mongo
    │   └── graficos.html
    └── utils/
        ├── db.py                 # Conexión MongoDB
        ├── sql_server.py         # Conexión SQL Server
        └── decorators.py         # login_required
```

---

## Configuración paso a paso

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd aa
```

### 2. Crear el archivo `.env`

Crea un archivo `.env` en la raíz del proyecto con este contenido (ajusta los valores a tu entorno):

```env
SECRET_KEY=una-clave-secreta-cualquiera
MONGO_URI=mongodb+srv://usuario:password@cluster.mongodb.net/?appName=Cluster0
DATABASE_NAME=sensores_mongo
ARDUINO_PORT=COM3
BAUD_RATE=9600
SQL_SERVER=NOMBRE_PC\SQLEXPRESS
SQL_DATABASE=sensores
```

> **Cómo encontrar el nombre de tu instancia SQL Server:**  
> Abre SQL Server Management Studio (SSMS) → el nombre que aparece en el campo "Server name" al conectarte es el valor de `SQL_SERVER` (ej. `DESKTOP-ABC123\SQLEXPRESS`).

### 3. Configurar SQL Server

Abre `schema_sensores.sql` en SSMS y ejecútalo completo (F5 o "Execute").  
El script:
- Crea la base de datos `sensores`
- Crea las 4 tablas: `dispositivos`, `zonas_riego`, `lecturas`, `umbrales_alerta`
- Inserta datos de prueba
- Crea la vista `vista_resumen_por_zona`
- Crea la función `dbo.fn_clasificar_humedad`
- Crea el procedimiento `dbo.sp_lecturas_por_zona`

> El script es seguro de ejecutar varias veces (tiene guards `DROP IF EXISTS`).

### 4. Poblar MongoDB

Desde la raíz del proyecto:

```bash
python poblar_mongo.py
```

Esto inserta en MongoDB Atlas:
- 3 documentos en `configuraciones` (uno por dispositivo Arduino)
- 14 documentos en `alertas` (con niveles crítico, advertencia y normal)

### 5. Ejecutar la aplicación Flask

```bash
cd SensoresWeb_MongoDB
python app.py
```

La app estará disponible en: **http://localhost:5000**

---

## Uso de la aplicación

### Crear un usuario

1. Ir a `http://localhost:5000/registro`
2. Ingresar nombre, correo y contraseña
3. El usuario queda guardado en MongoDB Atlas (colección `usuarios`)

### Navegar el sistema

| Ruta | Descripción |
|---|---|
| `/login` | Inicio de sesión |
| `/registro` | Registro de nuevo usuario |
| `/dashboard` | Tabla de lecturas en tiempo real (MongoDB) |
| `/graficos` | Gráficos por tipo de sensor |
| `/analisis` | **Página de integración:** datos de SQL Server + alertas de MongoDB |

### Página de análisis (`/analisis`)

Esta página demuestra la integración de ambos motores:

- **Resumen por Zona** — consume `vista_resumen_por_zona` (JOIN + GROUP BY en SQL Server)
- **Clasificar Humedad** — llama a `dbo.fn_clasificar_humedad()` con el valor ingresado
- **Lecturas por Zona** — ejecuta `EXEC dbo.sp_lecturas_por_zona` con el id de zona seleccionado
- **Log de Alertas** — consulta la colección `alertas` de MongoDB Atlas

---

## Scripts adicionales

### Exportar colecciones MongoDB a JSON

```bash
# Desde la raíz del proyecto
python exportar_mongo.py
```

Genera los archivos:
```
mongo_export/
├── usuarios.json
├── lecturas.json
├── configuraciones.json
└── alertas.json
```

### Recibir datos del Arduino (opcional)

```bash
# Desde SensoresWeb_MongoDB/
python guardar_datos.py
```

Lee datos del puerto serial del Arduino y guarda en SQL Server y MongoDB simultáneamente. Requiere Arduino conectado al puerto configurado en `ARDUINO_PORT` del `.env`.

---

## Endpoints de la API

### Datos desde MongoDB

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/datos` | Últimas lecturas de sensores (MongoDB) |
| GET | `/api/mongo/alertas` | Últimas 20 alertas |
| GET | `/api/mongo/configuraciones` | Configuraciones de dispositivos |

### Datos desde SQL Server

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/sql/resumen` | Resultado de `vista_resumen_por_zona` |
| GET | `/api/sql/zona/<id>` | Ejecuta `sp_lecturas_por_zona` para esa zona |
| GET | `/api/sql/humedad/<valor>` | Llama `fn_clasificar_humedad` con ese valor |

> Todos los endpoints requieren sesión activa (excepto `/api/datos`).

---

## Modelo de datos SQL Server

```
dispositivos ──────────────┐
  id PK                    │
  nombre                   │
  ubicacion                │
  tipo                     │
  fecha_instalacion        │
                           │
zonas_riego ───────────────┤
  id PK                    │
  nombre                   │
  tipo_cultivo             │
  descripcion              │
       │                   │
       ▼                   ▼
umbrales_alerta     lecturas
  id PK              id PK
  id_zona FK ◄─────  id_dispositivo FK
  variable           id_zona FK
  valor_min          fecha
  valor_max          temp_dht
  activo             humedad
                     temp_bmp
                     presion
                     luz
```

## Colecciones MongoDB

| Colección | Rol | Complementa a SQL |
|---|---|---|
| `usuarios` | Autenticación con esquema flexible | — |
| `lecturas` | Buffer de ingesta en tiempo real del Arduino | `lecturas` SQL (relacional vs. crudo) |
| `configuraciones` | Config por dispositivo con campos variables | `dispositivos` SQL (metadata dinámica) |
| `alertas` | Log de eventos con estructura variable | `umbrales_alerta` SQL (log de disparos) |

---

## Solución de problemas

**Error al conectar SQL Server:**  
Verifica que el valor de `SQL_SERVER` en `.env` coincide exactamente con el nombre de tu instancia. Abre SSMS y copia el nombre del servidor desde la pantalla de conexión.

**Error `pyodbc.Error: [IM002]`:**  
Instala ODBC Driver 17 for SQL Server desde el sitio de Microsoft.

**Error al importar `dotenv`:**  
```bash
pip install python-dotenv
```

**La colección `alertas` aparece vacía:**  
Ejecuta `python poblar_mongo.py` desde la raíz del proyecto antes de abrir `/analisis`.

**`guardar_datos.py` falla al iniciar:**  
El Arduino debe estar conectado antes de ejecutar el script. El puerto se configura con `ARDUINO_PORT` en `.env` (en Linux es `/dev/ttyUSB0` o similar, en Windows `COM3`, `COM4`, etc.).
