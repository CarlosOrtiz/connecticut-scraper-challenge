# Connecticut Scraper Challenge

Prueba técnica en Python para extraer información de:

- `Foreclosures` desde el portal judicial de Connecticut.
- `Tax Sales` desde `cttaxsales.com`, incluyendo descarga de PDFs y extracción con Gemini usando prompts dinámicos almacenados en MongoDB.

## Estructura

```text
connecticut-scraper-challenge
├─ .python-version
├─ README.md
├─ docker-compose.yml
├─ package-lock.json
├─ package.json
├─ prueba-tecnica-senior.md
├─ requirements.txt
├─ serverless.yml
├─ scripts
│  ├─ foreclosures
│  │  └─ main.py
│  └─ tax_sales
│     └─ main.py
├─ src
│  ├─ api
│  │  └─ foreclosures
│  │     └─ scrape
│  │        └─ post.py
│  ├─ common
│  │  ├─ config.py
│  │  ├─ gemini.py
│  │  ├─ logging_config.py
│  │  └─ scraper_client.py
│  ├─ consumer
│  │  └─ execution_logs_consumer.py
│  ├─ handlers
│  │  ├─ api_handler.py
│  │  ├─ lambda_handler.py
│  │  └─ sqs_handler.py
│  ├─ lambda
│  │  └─ scrape-tax-sales
│  │     └─ main.py
│  ├─ repositories
│  │  ├─ base_repository.py
│  │  ├─ execution_logs_repository.py
│  │  ├─ foreclosures_repository.py
│  │  ├─ prompts_repository.py
│  │  └─ tax_sales_repository.py
│  ├─ scrapers
│  │  ├─ foreclosures
│  │  │  ├─ city_parser.py
│  │  │  ├─ client.py
│  │  │  └─ normalize_property.py
│  │  └─ tax_sales
│  │     ├─ client.py
│  │     ├─ downloader.py
│  │     └─ parser.py
│  ├─ scripts
│  │  └─ seed_prompts.py
│  ├─ services
│  │  ├─ execution_logs_consumer.py
│  │  ├─ foreclosures_service.py
│  │  └─ tax_sales_service.py
│  └─ topic
│     └─ tax_sales_finished.py
└─ tests
   ├─ conftest.py
   ├─ foreclosures
   │  └─ test_normalize_property.py
   └─ tax_sales
      └─ test_parser.py

```

## Requisitos

- Python `3.12` para desarrollo local
- AWS Lambda configurado con Python `3.11` en despliegue
- Docker y Docker Compose
- MongoDB local o remoto
- API key de Gemini

## Setup Local

1. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate
```

1.1. Para desactivar el entorno virtual:

```bash
deactivate
```

2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Crear archivo `.env` en la raíz del proyecto.

Ejemplo:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=prueba_tecnica

GEMINI_API_KEY=tu_api_key
GEMINI_MODEL=gemini-2.5-flash-lite

BASE_URL_CT=https://sso.eservices.jud.ct.gov/Foreclosures/Public/
URL_CT_TAX=https://cttaxsales.com/upcoming-tax-sales/

SNS_TOPIC_ARN=arn:aws:sns:us-east-1:*account_id*:tax-sales-finished
```

4. Levantar MongoDB local con Docker:

```bash
docker compose up -d
```

## Seed de Prompts

Nota: este script se creó para inicializar los prompts en MongoDB sin tener que insertarlos manualmente. Más adelante podría reemplazarse por un CRUD o por un proceso de inicialización de base de datos.

Para crear los prompts en la colección `prompts` en MongoDB:

```bash
python src/scripts/seed_prompts.py
```

## Parte 1

### Ejecutar Foreclosures (con VPN)
#### Nota: Para ejecutar este script se necesita VPN
```bash
python scripts/foreclosures/main.py
```
> response: 

```bash
2026-03-30 19:06:00,007 - src.services.foreclosures_service - INFO - Iniciando scraper de Foreclosures...
2026-03-30 19:06:00,047 - src.services.foreclosures_service - INFO - Se encontraron 57 towns ya guardados en MongoDB: 
2026-03-30 19:06:01,045 - src.services.foreclosures_service - INFO - Se encontraron 81 ciudades para procesar: 
2026-03-30 19:06:01,046 - src.services.foreclosures_service - INFO - Extrayendo datos de: ANSONIA...
2026-03-30 19:06:01,233 - src.services.foreclosures_service - INFO - Omitiendo AVON: ya existe en MongoDB.
2026-03-30 19:06:01,233 - src.services.foreclosures_service - INFO - Omitiendo BERLIN: ya existe en MongoDB.
2026-03-30 19:06:01,233 - src.services.foreclosures_service - INFO - Omitiendo BOLTON: ya existe en MongoDB.
2026-03-30 19:06:01,233 - src.services.foreclosures_service - INFO - Extrayendo datos de: BRANFORD...
...
2026-03-30 19:06:06,704 - src.services.foreclosures_service - INFO - Extrayendo datos de: MERIDEN...
2026-03-30 19:06:06,923 - src.services.foreclosures_service - INFO - Omitiendo MIDDLEBURY: ya existe en MongoDB.
2026-03-30 19:06:06,923 - src.services.foreclosures_service - INFO - Omitiendo MIDDLEFIELD: ya existe en MongoDB.
2026-03-30 19:06:06,923 - src.services.foreclosures_service - INFO - Extrayendo datos de: MIDDLETOWN...
2026-03-30 19:06:07,223 - src.services.foreclosures_service - INFO - Omitiendo MILFORD: ya existe en MongoDB.
....
2026-03-30 19:06:07,224 - src.services.foreclosures_service - INFO - Omitiendo WOLCOTT: ya existe en MongoDB.
2026-03-30 19:06:07,224 - src.services.foreclosures_service - INFO - Guardando datos en MongoDB...
2026-03-30 19:06:07,260 - src.services.foreclosures_service - INFO - ✅ Proceso terminado. Modificados/Nuevos: 28
{
  "success": true,
  "modified_count": 0,
  "upserted_count": 28
}
```

### Ejecutar Tax Sales

```bash
python scripts/tax_sales/main.py
```
El proceso de `tax_sales`:

- scrapea la página de `upcoming tax sales`
- descarga los PDFs en `src/scrapers/tax_sales/downloads/`
- consulta prompts activos desde MongoDB
- ejecuta extracción con Gemini
- guarda resultados en la colección `tax_sales`

## Testing Local

Se configuró `pytest` para pruebas unitarias básicas.

### Ejecutar tests

```bash
pytest
```

### Ejecutar tests con cobertura

```bash
pytest --cov=src --cov-report=term-missing
```

Actualmente hay tests para:

- normalización de propiedades en `foreclosures`
- parseo del HTML de `tax_sales`

## Parte 2 - Adaptación a aws-python-helper

La Parte 2 adapta el código funcional a una estructura compatible con `aws-python-helper`.

### 2.1 Foreclosures vía API

Ruta esperada:

```text
POST /foreclosures/scrape
```

Archivos principales:

- `src/api/foreclosures/scrape/post.py`
- `src/handlers/api_handler.py`
- `src/services/foreclosures_service.py`

### 2.2 Tax Sales como Lambda Standalone

Lambda:

```text
scrape-tax-sales
```

Trigger esperado:

- EventBridge Schedule
- ejecución recurrente cada viernes

Archivos principales:

- `src/handlers/lambda_handler.py`
- `src/services/tax_sales_service.py`
- `src/lambda/scrape-tax-sales/main.py`

### 2.3 Repositories

Repositorios implementados:

- `src/repositories/foreclosures_repository.py`
- `src/repositories/tax_sales_repository.py`
- `src/repositories/prompts_repository.py`
- `src/repositories/execution_logs_repository.py`

### 2.4 Flujo SNS -> SQS

Implementado de forma opcional para registrar ejecuciones:

- la lambda `scrape-tax-sales` publica una notificación al finalizar
- un consumer SQS recibe el mensaje
- se guarda un registro en `execution_logs`

### 2.5 Handlers

Handlers declarados:

- `src/handlers/api_handler.py`
- `src/handlers/lambda_handler.py`
- `src/handlers/sqs_handler.py`

## Serverless

La intención de despliegue está declarada en:

- `serverless.yml`

Incluye:

- API para `foreclosures`
- lambda programada para `tax_sales`
- consumer SQS para `execution_logs`

## Colecciones MongoDB

Colecciones usadas:

- `foreclosures`
- `tax_sales`
- `prompts`
- `execution_logs`

## Notas

- Los prompts de Gemini no están hardcodeados en el scraper de `tax_sales`; se leen desde MongoDB.
- Solo se ejecutan prompts con `status: "active"`.
- Los PDFs ya descargados se omiten en ejecuciones posteriores.
- Se agregaron tests locales para facilitar validación sin desplegar en AWS.
