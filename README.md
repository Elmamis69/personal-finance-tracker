# 💰 Personal Finance Tracker

Sistema de seguimiento de gastos personales construido con FastAPI, MongoDB, InfluxDB y Grafana.

## 🏗️ Arquitectura

- **FastAPI**: API REST
- **MongoDB**: Base de datos principal (transacciones, presupuestos)
- **InfluxDB**: Time series database (métricas financieras)
- **Grafana**: Visualización de datos

## 📋 Requisitos

- Docker y Docker Compose
- Python 3.11+

## 🚀 Inicio Rápido

### 1. Configurar variables de entorno

```bash
cp .env.example .env
```

### 2. Levantar servicios con Docker

```bash
docker-compose up -d
```

Esto levantará:
- **MongoDB**: `http://localhost:27017`
- **InfluxDB**: `http://localhost:8086`
- **Grafana**: `http://localhost:3000`
- **API**: `http://localhost:8000`

### 3. Acceder a los servicios

- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **InfluxDB UI**: http://localhost:8086 (admin/adminpassword)

## 📁 Estructura del Proyecto

```
personal-finance-tracker/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/     # Endpoints de la API
│   ├── core/                  # Configuración central
│   ├── db/                    # Conexiones a bases de datos
│   ├── models/                # Modelos Pydantic
│   └── services/              # Lógica de negocio
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🎯 Archivos que Debes Crear

### 1. Configuración (`app/core/config.py`)
- Cargar variables de entorno
- Configuración de la aplicación

### 2. Conexiones DB (`app/db/`)
- `mongodb.py`: Cliente MongoDB
- `influxdb.py`: Cliente InfluxDB

### 3. Modelos (`app/models/`)
- `transaction.py`: Modelo de transacción
- `budget.py`: Modelo de presupuesto

### 4. Main (`app/main.py`)
- Inicializar FastAPI
- Registrar routers
- Lifecycle events (startup/shutdown)

### 5. Endpoints (`app/api/v1/endpoints/`)
- `health.py`: Health check
- `transactions.py`: CRUD transacciones
- `budgets.py`: CRUD presupuestos
- `analytics.py`: Métricas y analytics

### 6. Services (`app/services/`)
- `influx_service.py`: Escribir métricas a InfluxDB

## 💡 Casos de Uso

### Transacciones
- Crear transacción (ingreso/gasto)
- Listar transacciones con filtros
- Actualizar/eliminar transacciones
- Categorizar gastos

### Presupuestos
- Crear presupuesto mensual por categoría
- Monitorear progreso del presupuesto
- Alertas de exceso de presupuesto

### Analytics (InfluxDB)
- Gastos diarios/semanales/mensuales
- Gastos por categoría en el tiempo
- Comparación mes a mes
- Tasa de ahorro

## 🎨 Dashboard en Grafana

Métricas sugeridas:
1. **Gastos vs Ingresos** (línea temporal)
2. **Distribución por Categoría** (pie chart)
3. **Tendencia de Ahorro** (gauge)
4. **Top Categorías del Mes** (bar chart)
5. **Budget vs Real** (comparación)

## 🛠️ Comandos Útiles

```bash
# Ver logs
docker-compose logs -f api

# Reiniciar servicios
docker-compose restart

# Detener todo
docker-compose down

# Limpiar volúmenes
docker-compose down -v
```

## 🗺️ Roadmap del Proyecto

### Fase 1: Configuración Base 
- [x] Estructura de carpetas
- [x] Docker Compose (MongoDB, InfluxDB, Grafana)
- [x] Requirements y configuración inicial
- [x] `app/core/config.py` - Configuración con Pydantic Settings
- [x] `app/db/mongodb.py` - Conexión MongoDB con Motor
- [x] `app/db/influxdb.py` - Cliente InfluxDB
- [x] `app/main.py` - FastAPI app básica

### Fase 2: Modelos de Datos
- [x] `app/models/transaction.py` - Modelo de transacciones
- [x] `app/models/budget.py` - Modelo de presupuestos
- [x] Enums para categorías y tipos

### Fase 3: API Endpoints - Transacciones
- [x] `app/api/v1/endpoints/health.py` - Health check
- [x] `app/api/v1/endpoints/transactions.py` - CRUD básico
- [x] POST /transactions - Crear transacción
- [x] GET /transactions - Listar con filtros
- [x] GET /transactions/{id} - Obtener por ID
- [x] PUT /transactions/{id} - Actualizar
- [x] DELETE /transactions/{id} - Eliminar

### Fase 4: API Endpoints - Presupuestos
- [x] `app/api/v1/endpoints/budgets.py` - CRUD presupuestos
- [x] POST /budgets - Crear presupuesto mensual
- [x] GET /budgets - Listar presupuestos
- [x] GET /budgets/{id} - Obtener presupuesto
- [x] GET /budgets/{id}/progress - Progreso vs límite
- [x] PUT /budgets/{id} - Actualizar presupuesto
- [x] DELETE /budgets/{id} - Eliminar presupuesto

### Fase 5: Integración con InfluxDB
- [ ] `app/services/influx_service.py` - Servicio para métricas
- [ ] Escribir métricas al crear/actualizar transacciones
- [ ] Métricas: gastos diarios, por categoría, ingresos
- [ ] `app/api/v1/endpoints/analytics.py` - Endpoints de analytics
- [ ] GET /analytics/spending-trend - Tendencia de gastos
- [ ] GET /analytics/category-breakdown - Gastos por categoría
- [ ] GET /analytics/monthly-comparison - Comparación mensual
- [ ] GET /analytics/savings-rate - Tasa de ahorro

### Fase 6: Dashboards en Grafana
- [ ] Configurar datasource de InfluxDB
- [ ] Dashboard: Gastos vs Ingresos (time series)
- [ ] Dashboard: Distribución por Categoría (pie chart)
- [ ] Dashboard: Tendencia de Ahorro (gauge)
- [ ] Dashboard: Top 5 Categorías del Mes (bar chart)
- [ ] Dashboard: Budget vs Real por Categoría
- [ ] Dashboard: Alertas de exceso de presupuesto

### Fase 7: Características Avanzadas
- [ ] Filtros avanzados en transacciones (fecha, monto, categoría)
- [ ] Exportar transacciones a CSV
- [ ] Notificaciones cuando se excede presupuesto
- [ ] Metas de ahorro
- [ ] Categorías personalizadas
- [ ] Multi-moneda

### Fase 8: Testing y Documentación
- [ ] Tests unitarios para modelos
- [ ] Tests de integración para endpoints
- [ ] Tests para servicios de InfluxDB
- [ ] Documentación de API mejorada
- [ ] Ejemplos de uso en README

## 🤝 Contribución

Este es un proyecto personal de aprendizaje.
