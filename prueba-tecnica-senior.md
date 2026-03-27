# Prueba Tecnica — Desarrollador Senior Python

## Contexto

Trabajamos en una plataforma de busqueda de registros legales de propiedades en Connecticut. Nuestro stack principal es:

- **Python 3.12**
- **MongoDB** (Atlas)
- **Google Gemini API** para extraccion de datos de documentos PDF
- **Selenium / HTTP scraping** para extraccion de datos de sitios web
- **AWS Serverless** (Lambda, Fargate, SQS, SNS, API Gateway)
- **aws-python-helper** — framework interno para orquestar Lambda handlers, APIs, consumers y tareas

Esta prueba evalua tu capacidad para:
1. Construir scrapers funcionales de manera secuencial (scripts que funcionen)
2. Integrar con APIs de LLM usando prompts dinamicos almacenados en base de datos
3. Adaptar codigo funcional a un framework serverless siguiendo su documentacion

**Tiempo sugerido:** 4-6 horas (Parte 1: 2-3h, Parte 2: 2-3h)

---

## Requisitos Previos

| Herramienta | Version | Notas |
|---|---|---|
| Python | 3.12+ | |
| MongoDB | 6.0+ | Local (Docker) o MongoDB Atlas free tier |
| Google Gemini API Key | — | Obtener en https://aistudio.google.com/apikey (free tier es suficiente) |
| Git | — | Para entregar el codigo |

### Variables de entorno necesarias

```bash
MONGO_URI=mongodb://localhost:27017  # o tu connection string de Atlas
MONGO_DB_NAME=prueba_tecnica
GEMINI_API_KEY=tu_api_key_aqui
```

---

## Parte 1 — Scripts Secuenciales

El objetivo de esta parte es crear scripts Python funcionales que se ejecuten de manera secuencial. No necesitas infraestructura cloud, solo codigo que funcione localmente.

### Estructura de carpetas sugerida

```
prueba-tecnica/
├── scripts/
│   ├── foreclosures/
│   │   └── main.py
│   ├── tax_sales/
│   │   └── main.py
│   └── common/
│       ├── db.py              # Conexion y operaciones MongoDB
│       └── ai.py              # Cliente Gemini y ejecucion de prompts
├── requirements.txt
├── .env.example
└── README.md
```

---

### 1.1 Scraping de Foreclosures

**URL:** https://sso.eservices.jud.ct.gov/Foreclosures/Public/PendPostbyTownList.aspx

**Objetivo:** Extraer la informacion de foreclosures (ejecuciones hipotecarias) pendientes y/o posted que aparece en esta pagina, agrupada por municipio (town).

**Requisitos:**

- Scrappear la data de la pagina. Puedes usar la tecnica que prefieras: HTTP requests directos, Selenium, BeautifulSoup, o cualquier combinacion que consideres apropiada.
- Organizar la data tal como esta presentada en la pagina (agrupada por town).
- Cada registro debe contener, como minimo, los campos relevantes que la pagina muestra por cada foreclosure (analiza la pagina y determina cuales son).
- Guardar los resultados en una collection de MongoDB llamada `foreclosures`.
- El script debe ser ejecutable con: `python scripts/foreclosures/main.py`

**Se evalua:**
- Que el script funcione y extraiga datos reales
- Estructura del codigo (separacion de responsabilidades, funciones claras)
- Manejo de errores basico (conexion, timeouts, pagina no disponible)
- Reutilizacion del modulo `common/db.py` para la conexion a MongoDB

---

### 1.2 Scraping de Tax Sales con extraccion via Gemini

**URL:** https://cttaxsales.com/upcoming-tax-sales/

**Objetivo:** Extraer el listado de ventas fiscales (tax sales) proximas, descargar los PDFs asociados, y usar Google Gemini para extraer informacion estructurada de cada PDF.

**Requisitos:**

1. **Scraping de la pagina:**
   - Extraer el listado de upcoming tax sales con la informacion visible en la pagina.
   - Identificar y descargar los PDFs asociados a cada tax sale (guardarlos localmente en una carpeta `downloads/`).

2. **Prompts dinamicos desde MongoDB:**
   - Crear una collection `prompts` en MongoDB con al menos los siguientes documentos:

   ```json
   {
     "key": "amount_due",
     "question": "Extract the total amount due for this property from the document. Return only the numeric value without currency symbols.",
     "schema": {
       "type": "object",
       "properties": {
         "amount_due": { "type": "string" }
       },
       "required": ["amount_due"]
     },
     "status": "active"
   }
   ```

   ```json
   {
     "key": "property_address",
     "question": "Extract the full property address from this tax sale document.",
     "schema": {
       "type": "object",
       "properties": {
         "property_address": { "type": "string" }
       },
       "required": ["property_address"]
     },
     "status": "active"
   }
   ```

   - Puedes agregar mas prompts si lo consideras util (owner_name, sale_date, municipality, etc.).
   - **El codigo debe leer los prompts desde MongoDB en tiempo de ejecucion.** No deben estar hardcodeados en el script.
   - Solo se deben ejecutar los prompts con `status: "active"`.

3. **Extraccion con Gemini:**
   - Para cada PDF descargado, iterar sobre los prompts activos de MongoDB.
   - Enviar el PDF junto con cada prompt a la API de Gemini.
   - Usar el `schema` del prompt para que Gemini retorne una respuesta JSON estructurada.
   - Consolidar los resultados de todos los prompts por cada tax sale.

4. **Persistencia:**
   - Guardar los resultados en una collection `tax_sales` de MongoDB.
   - Cada documento debe contener la informacion del scraping de la pagina + los datos extraidos por Gemini de su PDF.

5. **Ejecucion:** `python scripts/tax_sales/main.py`

**Se evalua:**
- Funcionalidad completa (scraping + descarga de PDFs + extraccion con Gemini)
- Implementacion correcta de prompts dinamicos desde MongoDB (no hardcodeados)
- Reutilizacion de modulos compartidos (`common/db.py`, `common/ai.py`)
- Manejo de errores (PDFs que no se pueden descargar, rate limits de Gemini, respuestas invalidas)

---

## Parte 2 — Adaptacion al Framework aws-python-helper

En esta parte, debes tomar el codigo funcional de la Parte 1 y adaptarlo para que funcione dentro de la arquitectura de nuestro framework serverless: **aws-python-helper**.

**Documentacion del framework:** https://pypi.org/project/aws-python-helper/

Lee la documentacion del framework y adapta tu codigo segun sus convenciones de estructura de carpetas, nombres de archivos, clases base y handlers.

> **Nota:** No necesitas que el codigo se ejecute en AWS. Se evalua que la estructura, los nombres, las clases y los patrones sean coherentes con lo que el framework espera. Si la prueba esta organizada correctamente, deberia poder desplegarse sin modificaciones de estructura.

---

### 2.1 Foreclosures — Activable por API

Adapta el scraping de foreclosures para que sea invocable via una **API REST POST** en la ruta:

```
POST /foreclosures/scrape
```

- Debe usar un `ForeclosuresRepository` para persistir los datos.
- La logica de scraping debe estar separada en un modulo reutilizable (no directamente en la clase de la API).

---

### 2.2 Tax Sales — Proceso recurrente (Lambda Standalone)

Adapta el scraping de tax sales para que funcione como una **Lambda Standalone** llamada `scrape-tax-sales`.

- Esta Lambda se ejecutara de forma recurrente cada 7 dias (los viernes) via un EventBridge schedule.
- Debe usar `PromptsRepository` para consultar los prompts dinamicos y `TaxSalesRepository` para guardar resultados.

---

### 2.3 Repositories

Implementa los siguientes repositorios siguiendo el patron del framework:

| Repository | Collection | Descripcion |
|---|---|---|
| `ForeclosuresRepository` | `foreclosures` | Datos de ejecuciones hipotecarias |
| `TaxSalesRepository` | `tax_sales` | Datos de ventas fiscales |
| `PromptsRepository` | `prompts` | Prompts dinamicos para Gemini |
| `ExecutionLogsRepository` | `execution_logs` | Registros de ejecucion (ver seccion 2.4) |

---

### 2.4 Flujo SNS → SQS (Opcional)

Implementa un flujo de notificacion post-ejecucion:

1. Al finalizar el scraping de tax sales (Lambda del punto 2.2), publicar un mensaje a un **SNS Topic** que notifique la finalizacion.
2. Un **SQS Consumer** recibe ese mensaje y guarda un registro en la collection `execution_logs` con al menos:
   - Fecha y hora de inicio
   - Fecha y hora de fin
   - Cantidad de registros procesados
   - Estado (`success` / `error`)
   - Mensaje de error (si aplica)

---

### 2.5 Handlers

Declara los handlers necesarios segun los componentes que hayas implementado (API, Lambda, SQS consumer). Revisa la documentacion del framework para entender como se declaran.

---

## Bonus (Opcional)

Estos puntos son extras opcionales. No son requisito, pero suman.

- **Testing local:** Configurar un entorno que permita probar el codigo adaptado al framework localmente (Docker Compose con MongoDB, mocks, pytest, o cualquier solucion que consideres). Si logras implementar esto, documenta como ejecutarlo en el README.
- **Manejo avanzado de errores:** Reintentos con backoff exponencial para Gemini, manejo de PDFs corruptos o vacios.
- **Type hints completos** en funciones y retornos.
- **Logs estructurados** con el modulo `logging` de Python.

---

## Criterios de Evaluacion

| Criterio | Peso | Descripcion |
|---|---|---|
| **Funcionalidad** | 30% | El codigo de la Parte 1 se ejecuta y produce resultados correctos |
| **Arquitectura y codigo** | 25% | Separacion de responsabilidades, codigo limpio, modulos reutilizables |
| **Adaptacion al framework** | 25% | La Parte 2 sigue correctamente las convenciones de aws-python-helper |
| **Prompts dinamicos** | 10% | Implementacion correcta de prompts desde MongoDB (no hardcodeados) |
| **Extras / Bonus** | 10% | Testing local, manejo avanzado de errores, documentacion |

---

## Entregables

- Repositorio Git (GitHub, GitLab o Bitbucket) con historial de commits
- `README.md` con instrucciones claras de setup y ejecucion
- `.env.example` con las variables de entorno necesarias
- `requirements.txt` completo
- Commits atomicos con mensajes descriptivos

---

**Exitos!**
