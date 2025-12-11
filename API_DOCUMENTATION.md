# 📖 API Documentation - Personal Finance Tracker

## 🌐 Base URL

```
http://localhost:8000
```

## 📑 Tabla de Contenidos

- [Health Endpoints](#health-endpoints)
- [Transactions Endpoints](#transactions-endpoints)
- [Budgets Endpoints](#budgets-endpoints)
- [Analytics Endpoints](#analytics-endpoints)
- [Modelos de Datos](#modelos-de-datos)
- [Códigos de Estado](#códigos-de-estado)
- [Ejemplos de Uso](#ejemplos-de-uso)

---

## 🏥 Health Endpoints

### GET `/`
Mensaje de bienvenida de la API.

**Response:**
```json
{
  "message": "Welcome to Personal Finance Tracker API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### GET `/health`
Verifica el estado de salud de la API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-11T10:30:00"
}
```

### GET `/health/db`
Verifica la conexión con las bases de datos.

**Response:**
```json
{
  "mongodb": "connected",
  "influxdb": "connected"
}
```

---

## 💰 Transactions Endpoints

### POST `/api/v1/transactions`
Crea una nueva transacción.

**Request Body:**
```json
{
  "amount": 150.50,
  "type": "expense",
  "category": "food",
  "description": "Groceries at supermarket",
  "date": "2025-12-11T10:00:00",
  "tags": ["groceries", "weekly"]
}
```

**Campos:**
- `amount` (float, required): Monto > 0
- `type` (string, required): "income" o "expense"
- `category` (string, required): Ver [categorías disponibles](#categorías)
- `description` (string, required): 1-500 caracteres
- `date` (datetime, optional): Por defecto es la fecha actual
- `tags` (array, optional): Lista de etiquetas

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "amount": 150.50,
  "type": "expense",
  "category": "food",
  "description": "Groceries at supermarket",
  "date": "2025-12-11T10:00:00",
  "tags": ["groceries", "weekly"],
  "created_at": "2025-12-11T10:00:00",
  "updated_at": "2025-12-11T10:00:00"
}
```

### GET `/api/v1/transactions`
Lista todas las transacciones con filtros opcionales.

**Query Parameters:**
- `type` (string, optional): Filtrar por tipo ("income" o "expense")
- `category` (string, optional): Filtrar por categoría
- `start_date` (datetime, optional): Fecha inicio
- `end_date` (datetime, optional): Fecha fin
- `tags` (string, optional): Filtrar por etiqueta
- `skip` (int, optional): Saltar N registros (default: 0)
- `limit` (int, optional): Límite de registros (default: 100, max: 1000)

**Ejemplo:**
```
GET /api/v1/transactions?type=expense&category=food&limit=10
```

**Response:** `200 OK`
```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "amount": 150.50,
    "type": "expense",
    "category": "food",
    "description": "Groceries at supermarket",
    "date": "2025-12-11T10:00:00",
    "tags": ["groceries", "weekly"],
    "created_at": "2025-12-11T10:00:00",
    "updated_at": "2025-12-11T10:00:00"
  }
]
```

### GET `/api/v1/transactions/{transaction_id}`
Obtiene una transacción específica.

**Response:** `200 OK` o `404 Not Found`

### PUT `/api/v1/transactions/{transaction_id}`
Actualiza una transacción existente.

**Request Body:** (todos los campos opcionales)
```json
{
  "amount": 200.00,
  "description": "Updated description",
  "tags": ["updated", "tag"]
}
```

**Response:** `200 OK` o `404 Not Found`

### DELETE `/api/v1/transactions/{transaction_id}`
Elimina una transacción.

**Response:** `204 No Content` o `404 Not Found`

---

## 💵 Budgets Endpoints

### POST `/api/v1/budgets`
Crea un nuevo presupuesto.

**Request Body:**
```json
{
  "category": "food",
  "limit_amount": 2000.00,
  "period": "monthly",
  "start_date": "2025-12-01T00:00:00",
  "end_date": "2025-12-31T23:59:59",
  "alert_threshold": 0.8
}
```

**Campos:**
- `category` (string, required): Categoría del presupuesto
- `limit_amount` (float, required): Límite del presupuesto > 0
- `period` (string, optional): "weekly", "monthly", "yearly" (default: "monthly")
- `start_date` (datetime, required): Fecha de inicio
- `end_date` (datetime, required): Fecha de fin
- `alert_threshold` (float, optional): Umbral de alerta 0-1 (default: 0.8)

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439012",
  "category": "food",
  "limit_amount": 2000.00,
  "period": "monthly",
  "start_date": "2025-12-01T00:00:00",
  "end_date": "2025-12-31T23:59:59",
  "alert_threshold": 0.8,
  "created_at": "2025-12-11T10:00:00",
  "updated_at": "2025-12-11T10:00:00"
}
```

### GET `/api/v1/budgets`
Lista todos los presupuestos con filtros opcionales.

**Query Parameters:**
- `category` (string, optional): Filtrar por categoría
- `period` (string, optional): Filtrar por periodo
- `active` (bool, optional): Solo presupuestos activos

**Response:** `200 OK`

### GET `/api/v1/budgets/{budget_id}`
Obtiene un presupuesto específico.

**Response:** `200 OK` o `404 Not Found`

### GET `/api/v1/budgets/{budget_id}/progress`
Obtiene el progreso actual del presupuesto.

**Response:** `200 OK`
```json
{
  "spent_amount": 1200.00,
  "remaining_amount": 800.00,
  "percentage_used": 60.0,
  "status": "safe",
  "is_over_budget": false
}
```

**Estados posibles:**
- `safe`: Gasto < umbral de alerta
- `warning`: Gasto >= umbral de alerta
- `critical`: Gasto >= 95% del límite
- `exceeded`: Gasto > límite

### PUT `/api/v1/budgets/{budget_id}`
Actualiza un presupuesto existente.

**Request Body:** (campos opcionales)
```json
{
  "limit_amount": 2500.00,
  "alert_threshold": 0.9
}
```

**Response:** `200 OK` o `404 Not Found`

### DELETE `/api/v1/budgets/{budget_id}`
Elimina un presupuesto.

**Response:** `204 No Content` o `404 Not Found`

---

## 📊 Analytics Endpoints

### GET `/api/v1/analytics/spending-trend`
Obtiene la tendencia de gastos en un periodo.

**Query Parameters:**
- `start_date` (datetime, required): Fecha inicio
- `end_date` (datetime, required): Fecha fin

**Ejemplo:**
```
GET /api/v1/analytics/spending-trend?start_date=2025-12-01T00:00:00&end_date=2025-12-31T23:59:59
```

**Response:** `200 OK`
```json
[
  {
    "date": "2025-12-01",
    "amount": 150.50
  },
  {
    "date": "2025-12-02",
    "amount": 200.00
  }
]
```

### GET `/api/v1/analytics/category-breakdown`
Obtiene el desglose de gastos por categoría.

**Query Parameters:**
- `start_date` (datetime, required)
- `end_date` (datetime, required)

**Response:** `200 OK`
```json
[
  {
    "category": "food",
    "total": 1500.00,
    "percentage": 45.5
  },
  {
    "category": "transport",
    "total": 800.00,
    "percentage": 24.2
  }
]
```

### GET `/api/v1/analytics/income-vs-expenses`
Compara ingresos vs gastos en un periodo.

**Query Parameters:**
- `start_date` (datetime, required)
- `end_date` (datetime, required)

**Response:** `200 OK`
```json
{
  "income": 5000.00,
  "expenses": 3200.00,
  "net": 1800.00,
  "savings_rate": 36.0
}
```

### GET `/api/v1/analytics/monthly-comparison`
Compara el mes actual vs el mes anterior.

**Response:** `200 OK`
```json
{
  "current_month": {
    "income": 5000.00,
    "expenses": 3000.00,
    "net": 2000.00
  },
  "last_month": {
    "income": 4800.00,
    "expenses": 3200.00,
    "net": 1600.00
  },
  "change_percentage": {
    "income": 4.17,
    "expenses": -6.25,
    "net": 25.0
  }
}
```

### GET `/api/v1/analytics/savings-rate`
Calcula la tasa de ahorro en un periodo.

**Query Parameters:**
- `start_date` (datetime, required)
- `end_date` (datetime, required)

**Response:** `200 OK`
```json
{
  "income": 5000.00,
  "expenses": 3000.00,
  "savings": 2000.00,
  "savings_rate": 40.0
}
```

---

## 📋 Modelos de Datos

### Categorías

**Categorías de Ingreso:**
- `salary` - Salario
- `freelance` - Trabajo independiente
- `investment` - Inversiones
- `gift` - Regalo
- `other_income` - Otro ingreso

**Categorías de Gasto:**
- `food` - Comida
- `transport` - Transporte
- `housing` - Vivienda
- `utilities` - Servicios
- `entertainment` - Entretenimiento
- `healthcare` - Salud
- `education` - Educación
- `shopping` - Compras
- `travel` - Viajes
- `insurance` - Seguros
- `other_expense` - Otro gasto

### Tipos de Transacción

```typescript
enum TransactionType {
  income = "income",
  expense = "expense"
}
```

### Periodos de Presupuesto

```typescript
enum BudgetPeriod {
  weekly = "weekly",
  monthly = "monthly",
  yearly = "yearly"
}
```

### Estados de Presupuesto

```typescript
enum BudgetStatus {
  safe = "safe",           // < 80% (o umbral configurado)
  warning = "warning",     // >= 80%
  critical = "critical",   // >= 95%
  exceeded = "exceeded"    // > 100%
}
```

---

## 🔢 Códigos de Estado

| Código | Descripción |
|--------|-------------|
| `200` | OK - Solicitud exitosa |
| `201` | Created - Recurso creado exitosamente |
| `204` | No Content - Recurso eliminado exitosamente |
| `400` | Bad Request - Datos inválidos |
| `404` | Not Found - Recurso no encontrado |
| `422` | Unprocessable Entity - Error de validación |
| `500` | Internal Server Error - Error del servidor |

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Registrar un Gasto

```bash
curl -X POST "http://localhost:8000/api/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 45.50,
    "type": "expense",
    "category": "food",
    "description": "Lunch at restaurant",
    "tags": ["dining", "work"]
  }'
```

### Ejemplo 2: Crear Presupuesto Mensual

```bash
curl -X POST "http://localhost:8000/api/v1/budgets" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "food",
    "limit_amount": 2000.00,
    "period": "monthly",
    "start_date": "2025-12-01T00:00:00",
    "end_date": "2025-12-31T23:59:59",
    "alert_threshold": 0.8
  }'
```

### Ejemplo 3: Ver Progreso del Presupuesto

```bash
curl -X GET "http://localhost:8000/api/v1/budgets/{budget_id}/progress"
```

### Ejemplo 4: Filtrar Transacciones

```bash
# Gastos de comida en diciembre
curl -X GET "http://localhost:8000/api/v1/transactions?type=expense&category=food&start_date=2025-12-01T00:00:00&end_date=2025-12-31T23:59:59"
```

### Ejemplo 5: Análisis de Gastos

```bash
# Tendencia de gastos del mes
curl -X GET "http://localhost:8000/api/v1/analytics/spending-trend?start_date=2025-12-01T00:00:00&end_date=2025-12-31T23:59:59"

# Desglose por categoría
curl -X GET "http://localhost:8000/api/v1/analytics/category-breakdown?start_date=2025-12-01T00:00:00&end_date=2025-12-31T23:59:59"

# Tasa de ahorro
curl -X GET "http://localhost:8000/api/v1/analytics/savings-rate?start_date=2025-12-01T00:00:00&end_date=2025-12-31T23:59:59"
```

---

## 🔐 Autenticación

**Nota:** Esta versión actual no implementa autenticación. En producción se recomienda agregar:
- JWT tokens
- OAuth2
- Rate limiting
- API keys

---

## 📝 Notas Adicionales

### Validaciones

- Los montos deben ser mayores a 0
- Las descripciones tienen un máximo de 500 caracteres
- Las fechas de fin deben ser posteriores a las de inicio
- El alert_threshold debe estar entre 0 y 1

### Paginación

Para endpoints que retornan listas, usa los parámetros:
- `skip`: Número de registros a saltar (default: 0)
- `limit`: Máximo de registros a retornar (default: 100, max: 1000)

### Formatos de Fecha

Todas las fechas deben estar en formato ISO 8601:
```
2025-12-11T10:30:00
```

---

## 🚀 Documentación Interactiva

La API incluye documentación interactiva automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estas interfaces permiten:
- Explorar todos los endpoints
- Probar requests directamente desde el navegador
- Ver esquemas de datos
- Descargar especificación OpenAPI

---

## 📞 Soporte

Para más información, consulta:
- [README.md](./README.md) - Guía de inicio
- [TESTING.md](./TESTING.md) - Documentación de tests
- Swagger UI en `/docs` - Documentación interactiva
