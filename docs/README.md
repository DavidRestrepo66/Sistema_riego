# Documentación · Sistema de Monitoreo de Sensores IoT

Índice de la documentación del proyecto final de Bases de Datos 2.

---

## Para quien necesita…

| Si quieres… | Lee… |
|-------------|------|
| Levantar el proyecto desde cero | [`instalacion.md`](instalacion.md) |
| Entender cómo se conectan los componentes | [`arquitectura.md`](arquitectura.md) |
| Ver el modelo de datos (ERD + colecciones) | [`bases_de_datos.md`](bases_de_datos.md) |
| Consumir la API REST | [`api.md`](api.md) |
| Usar la aplicación web | [`manual_usuario.md`](manual_usuario.md) |
| Preparar la presentación oral | [`presentacion_guion.md`](presentacion_guion.md) |

---

## Mapa de la documentación

```
docs/
├── README.md                ◄── ESTE archivo (índice)
├── instalacion.md           ◄── Setup paso a paso + troubleshooting
├── arquitectura.md          ◄── Capas, flujos y diagramas de componentes
├── bases_de_datos.md        ◄── ERD SQL Server + esquemas MongoDB
├── api.md                   ◄── Referencia REST completa
├── manual_usuario.md        ◄── Guía para el usuario final de la web
└── presentacion_guion.md    ◄── Guion para 3 estudiantes (con tiempos)
```

---

## Acerca del proyecto

**Sistema de Monitoreo de Sensores IoT — Riego Agrícola**
Aplicación web Flask que integra **SQL Server** (modelo relacional) y **MongoDB Atlas** (modelo documental) para monitorear sensores Arduino en zonas de cultivo.

- **Capa de adquisición:** Arduino (DHT22 + BMP280 + LDR) o simulador
- **Capa de datos:** doble persistencia SQL + MongoDB
- **Capa de aplicación:** Flask con arquitectura por capas (routes → services → repositories)
- **Capa de presentación:** dashboard responsive con Chart.js

Para una explicación completa empieza por [`arquitectura.md`](arquitectura.md).

---

## Resumen ultra-corto

```bash
# 1. Setup
cp .env.example .env       # editar con tus credenciales
pip install flask pymongo pyodbc python-dotenv bcrypt pyserial

# 2. Bases de datos
sqlcmd -i schema_sensores.sql   # o ejecutar en SSMS
python poblar_mongo.py

# 3. Aplicación
cd SensoresWeb_MongoDB
python app.py
# → http://localhost:5000
```

En el dashboard pulsa **"Simular Arduino"** para verificar que ambas bases escriben sin necesidad de hardware.
