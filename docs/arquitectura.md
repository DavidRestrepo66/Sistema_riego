# Arquitectura del Sistema

Sistema IoT de monitoreo de sensores agrícolas con doble persistencia (SQL Server + MongoDB Atlas) y aplicación web Flask.

---

## 1. Visión general por capas

```mermaid
flowchart TB
    subgraph ADQ["Capa de adquisición"]
        ARDUINO[Arduino<br/>DHT22 + BMP280 + LDR]
        SIM[simular_arduino.py<br/>generador de datos]
        GUARDAR[guardar_datos.py<br/>puente serial → DBs]
    end

    subgraph DATA["Capa de datos"]
        SQL[(SQL Server<br/>dispositivos, zonas_riego,<br/>lecturas, umbrales_alerta)]
        MONGO[(MongoDB Atlas<br/>usuarios, lecturas,<br/>configuraciones, alertas)]
    end

    subgraph APP["Capa de aplicación · Flask"]
        ROUTES[routes/<br/>auth · sensor · sql · mongo · view]
        SERVICES[services/<br/>lógica de negocio]
        REPOS[repositories/<br/>acceso a datos]
    end

    subgraph PRES["Capa de presentación"]
        BROWSER[Navegador<br/>Jinja2 + Chart.js]
    end

    ARDUINO -- USB Serial --> GUARDAR
    SIM -.alternativa.-> GUARDAR
    GUARDAR --> SQL
    GUARDAR --> MONGO

    ROUTES --> SERVICES --> REPOS
    REPOS --> SQL
    REPOS --> MONGO
    BROWSER <-- HTTP/JSON --> ROUTES
    BROWSER -- "POST /api/simular" --> ROUTES
```

---

## 2. Flujo de una lectura

```mermaid
sequenceDiagram
    participant A as Arduino
    participant G as guardar_datos.py
    participant M as MongoDB Atlas
    participant S as SQL Server
    participant F as Flask App
    participant B as Browser

    A->>G: "22.5,65.3,22.1,1013.2,420.0" (CSV)
    G->>G: parse + datetime.now()
    par
        G->>M: insert_one(lectura)
        M-->>G: ack
    and
        G->>S: INSERT INTO lecturas (...)
        S-->>G: ack
    end

    B->>F: GET /api/datos
    F->>M: find().sort(fecha, -1)
    M-->>F: documentos
    F-->>B: JSON

    B->>F: GET /api/sql/resumen
    F->>S: SELECT * FROM vista_resumen_por_zona
    S-->>F: filas
    F-->>B: JSON
```

---

## 3. Flujo del simulador (sin Arduino)

```mermaid
sequenceDiagram
    participant B as Browser
    participant F as Flask /api/simular
    participant M as MongoDB Atlas
    participant S as SQL Server

    B->>F: POST /api/simular {n: 5}
    loop n veces
        F->>F: random.uniform(...) → lectura
        F->>M: insert_one(lectura)
        M-->>F: ack
        F->>S: INSERT INTO lecturas (...)
        S-->>F: ack
    end
    F-->>B: {mongo: {ok: 5}, sql: {ok: 5}}
    B->>B: toast verde + refresh KPIs
```

---

## 4. Estructura de carpetas con responsabilidades

```
SensoresWeb_MongoDB/
├── app.py              ◄── Entry point: crea Flask, registra blueprints
├── config.py           ◄── Lee .env y expone Config
│
├── routes/             ── CAPA HTTP (recibe request → llama service)
│   ├── auth_routes.py     /login /registro /logout
│   ├── view_routes.py     /dashboard /analisis /graficos
│   ├── sensor_routes.py   /api/datos /api/simular
│   ├── sql_routes.py      /api/sql/*
│   └── mongo_routes.py    /api/mongo/*
│
├── services/           ── CAPA DE NEGOCIO (orquesta repositories)
│   ├── auth_service.py    hashing bcrypt, validaciones
│   ├── sensor_service.py  delega a sensor_repository
│   ├── serial_service.py  (futuro) ingesta serial encapsulada
│   └── sql_service.py     orquesta sql_repository
│
├── repositories/       ── CAPA DE ACCESO A DATOS
│   ├── sensor_repository.py      MongoDB: lecturas
│   ├── user_repository.py        MongoDB: usuarios
│   ├── sql_repository.py         SQL Server: vista, SP, función
│   └── mongo_extra_repository.py MongoDB: alertas, configuraciones
│
├── utils/              ── INFRAESTRUCTURA
│   ├── db.py              cliente MongoDB
│   ├── sql_server.py      conexión pyodbc a SQL Server
│   └── decorators.py      @login_required
│
├── templates/          ── VISTAS (Jinja2)
└── static/             ── CSS, JS, assets
```

---

## 5. Patrón Repository

Cada motor de base de datos tiene su propio repositorio. Las rutas **nunca** acceden directamente a las bases de datos — pasan por servicios, que delegan en repositorios.

| Capa | Sabe sobre HTTP | Sabe sobre lógica de negocio | Sabe sobre la BD |
|------|:--:|:--:|:--:|
| `routes/`       | ✅ | ❌ | ❌ |
| `services/`     | ❌ | ✅ | ❌ |
| `repositories/` | ❌ | ❌ | ✅ |

**Ventaja:** si mañana se cambia MongoDB por PostgreSQL para una colección, solo se reescribe el repositorio correspondiente — ni el servicio ni la ruta se enteran.

---

## 6. Estrategia de doble persistencia

**¿Por qué guardar la misma lectura en dos bases?**

| Aspecto | SQL Server | MongoDB |
|---------|-----------|---------|
| Rol de la lectura | Fuente de verdad relacional (con FK a `dispositivos`/`zonas_riego`) | Buffer crudo de ingesta |
| Garantía | Integridad referencial estricta | Disponibilidad inmediata aunque SQL esté caído |
| Consumo | Análisis: vistas, GROUP BY, JOINs | Streaming en vivo al dashboard |

**El `/api/simular`** ejecuta exactamente el mismo flujo que el Arduino real (parse → MongoDB → SQL Server) pero con datos generados, lo que permite validar todo el sistema sin hardware.

---

## 7. Resumen visual

```mermaid
flowchart LR
    subgraph INGESTA["Ingesta"]
        direction TB
        A[Arduino o Simulador]
    end

    subgraph PERSIST["Doble persistencia"]
        direction TB
        SQL[(SQL Server<br/>relacional)]
        MONGO[(MongoDB<br/>documental)]
    end

    subgraph WEB["Interfaz web"]
        direction TB
        DASH[Dashboard<br/>tiempo real]
        ANAL[Análisis<br/>vista · SP · función]
        GRAF[Gráficos]
    end

    A --> SQL
    A --> MONGO
    MONGO --> DASH
    SQL --> ANAL
    MONGO --> ANAL
    MONGO --> GRAF
```

Para más detalle del modelo de datos ver [`bases_de_datos.md`](bases_de_datos.md).
