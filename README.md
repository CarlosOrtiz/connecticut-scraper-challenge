# Connecticut Scraper Challenge

Prueba técnica en Python para extraer información de:

- `Foreclosures` desde el portal judicial de Connecticut.
- `Tax Sales` desde `cttaxsales.com`, incluyendo descarga de PDFs y extracción con Gemini usando prompts dinámicos almacenados en MongoDB.

## Estructura

```text
connecticut-scraper-challenge
├── README.md
├── docker-compose.yml
├── requirements.txt
├── serverless.yml
├── scripts
│   ├── common
│   ├── foreclosures
│   ├── tax_sales
│   └── seed_prompts.py
├── src
│   ├── api
│   ├── handlers
│   ├── repositories
│   └── services
└── tests
```

## Requisitos

- Python `3.12`
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
```

4. Levantar MongoDB local con Docker:

```bash
docker compose up -d
```

## Seed de Prompts
# Nota: se creo solo para no crearlos manualmente, o por un endpoint en el futuro se puede agregar un CRUD de prompts

Para crear los prompts en la colección `prompts` en MongoDB:

```bash
python -m scripts.seed_prompts
```

## Parte 1

### Ejecutar Foreclosures (con VPN)
# Nota: Para ejecutar este script se necesita VPN
```bash
python scripts/foreclosures/main.py
```

### Ejecutar Tax Sales

```bash
python scripts/tax_sales/main.py
```

El proceso de `tax_sales`:

- scrapea la página de `upcoming tax sales`
- descarga los PDFs en [`scripts/tax_sales/downloads/`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/scripts/tax_sales/downloads)
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
pytest --cov=scripts --cov-report=term-missing
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

- [`src/api/foreclosures/scrape/post.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/api/foreclosures/scrape/post.py)
- [`src/handlers/api_handler.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/handlers/api_handler.py)
- [`scripts/foreclosures/service.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/scripts/foreclosures/service.py)

### 2.2 Tax Sales como Lambda Standalone

Lambda:

```text
scrape-tax-sales
```

Trigger esperado:

- EventBridge Schedule
- ejecución recurrente cada viernes

Archivos principales:

- [`src/handlers/scrape_tax_sales_handler.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/handlers/scrape_tax_sales_handler.py)
- [`scripts/tax_sales/service.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/scripts/tax_sales/service.py)

### 2.3 Repositories

Repositorios implementados:

- [`src/repositories/foreclosures_repository.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/repositories/foreclosures_repository.py)
- [`src/repositories/tax_sales_repository.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/repositories/tax_sales_repository.py)
- [`src/repositories/prompts_repository.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/repositories/prompts_repository.py)
- [`src/repositories/execution_logs_repository.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/repositories/execution_logs_repository.py)

### 2.4 Flujo SNS -> SQS

Implementado de forma opcional para registrar ejecuciones:

- la lambda `scrape-tax-sales` publica una notificación al finalizar
- un consumer SQS recibe el mensaje
- se guarda un registro en `execution_logs`

### 2.5 Handlers

Handlers declarados:

- [`src/handlers/api_handler.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/handlers/api_handler.py)
- [`src/handlers/scrape_tax_sales_handler.py`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/src/handlers/scrape_tax_sales_handler.py)
- consumer SQS para logs de ejecución

## Serverless

La intención de despliegue está declarada en:

- [`serverless.yml`](/Users/caol/Documents/Projects/Technical/connecticut-scraper-challenge/serverless.yml)

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
