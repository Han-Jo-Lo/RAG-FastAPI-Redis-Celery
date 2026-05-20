# RAG con FastAPI, Celery y Redis

Sistema RAG (Retrieval-Augmented Generation) escalable y de alta performance con API REST, procesamiento asincrónico y caché distribuido.

## 📋 Descripción

Este proyecto implementa un **sistema inteligente de respuestas basadas en documentos** con arquitectura empresarial. Permite procesar múltiples documentos PDF, almacenarlos en bases de datos vectoriales independientes, y responder preguntas de forma asincrónica con gestión de memoria conversacional.

## ✨ Características

- ✅ **API REST con FastAPI** - Endpoints modernos y documentados automáticamente
- ✅ **Procesamiento Asincrónico** - Celery + Redis para no bloquear requests
- ✅ **Múltiples Bases de Datos** - Una por usuario/documento
- ✅ **Gestión de Memoria** - Histórico de conversaciones por usuario
- ✅ **LLM Inteligente** - GPT-4o-mini con embeddings de OpenAI
- ✅ **Caching Distribuido** - Redis para mejorar performance
- ✅ **Upload de Documentos** - Procesamiento automático de PDFs
- ✅ **Búsqueda Semántica** - ChromaDB para similitud vectorial
- ✅ **LangGraph** - Grafo en dos pasos: recuperación de contexto y respuesta con historial completo

## 🛠️ Arquitectura

```
Cliente (HTTP)
    ↓
FastAPI (main.py)
    ↓
Celery Worker (tasks.py)
    ↓
LangGraph (graph.py): context → chatbot
    ↓
    ├─ Vector Store (ChromaDB) — retrieve en nodo context
    ├─ LLM (GPT-4o-mini) — system + contexto + historial en chatbot
    ├─ Memory (Redis — historial por user_id)
    └─ Redis (Broker / backend Celery según .env)
```

## 📦 Requisitos

### Mínimos del Sistema
- Python 3.9+
- Redis 6.0+
- OpenAI API Key

### Dependencias

```
langchain==0.1.x
langchain_community
langchain-openai
langchain_experimental
langgraph
python-dotenv
pypdf
chromadb
fastapi
redis
celery
uvicorn
python-multipart
```

## 🚀 Instalación Rápida

### 1. Clonar/Descargar Proyecto

```bash
cd RAG-semantico-con-FastAPI-Celery-y-Redis
```

### 2. Crear Entorno Virtual

**PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**CMD:**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
EMBEDDING_MODEL=text-embedding-ada-002
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Application Settings
UPLOAD_DIR=./uploads
DATABASE_DIR=./databases
VECTOR_DB_BASE_PATH=./vector_stores
LOG_LEVEL=INFO
```

### 5. Iniciar Redis

**Opción 1: Redis ya instalado**
```bash
redis-server
```

**Opción 2: Docker (si tienes Docker instalado)**
```bash
docker run -d -p 6379:6379 redis:latest
```

**Opción 3: WSL (Windows)**
```bash
wsl redis-server
```

### 6. Iniciar la Aplicación

**Terminal 1 - Servidor FastAPI:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
celery -A celery_app worker --loglevel=info
```

El servidor estará disponible en: **http://localhost:8000**

Documentación automática (Swagger): **http://localhost:8000/docs**

## 📡 Endpoints API

### 1️⃣ Chat Asincrónico

Envía una pregunta y recibe un ID de tarea para consultar después.

```http
POST /chat
Content-Type: application/json

{
  "user_id": "user123",
  "message": "¿Cuáles son los términos y condiciones?",
  "database_name": "rappi"
}
```

**Respuesta (202 Accepted):**
```json
{
  "task_id": "abc123def456-789xyz",
  "status": "queued"
}
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "¿Cuáles son los términos de servicio?",
    "database_name": "mi_documento"
  }'
```

**Python:**
```python
import requests

response = requests.post('http://localhost:8000/chat', json={
    'user_id': 'user123',
    'message': '¿Cuáles son los términos?',
    'database_name': 'rappi'
})

task_id = response.json()['task_id']
print(f"Task ID: {task_id}")
```

### 2️⃣ Consultar Resultado de Tarea

Obtén el resultado usando el ID de la tarea.

```http
GET /result/{task_id}
```

**Respuesta (si está completa):**
```json
{
  "result_status": "SUCCESS",
  "result": "Los términos y condiciones establecen que..."
}
```

**Estados posibles:**
- `PENDING` - Tarea en cola, esperando procesamiento
- `STARTED` - Procesándose actualmente
- `SUCCESS` - Completada exitosamente
- `FAILURE` - Error durante procesamiento
- `RETRY` - Reintentando

**cURL:**
```bash
curl "http://localhost:8000/result/abc123def456-789xyz"
```

**Python:**
```python
import requests

result = requests.get(f'http://localhost:8000/result/{task_id}')
data = result.json()

print(f"Estado: {data['result_status']}")
print(f"Respuesta: {data['result']}")
```

### 3️⃣ Subir Documento

Carga un PDF nuevo para procesarlo.

```http
POST /upload
Content-Type: multipart/form-data

file: <binary PDF data>
```

**Respuesta (202 Accepted):**
```json
{
  "task_id": "ac619b1f-6468-4ecb-a547-8cc666fa1361",
  "status": "queued"
}
```

El procesamiento del documento ahora es asíncrono con Celery.  
Para conocer el resultado final del upload, consulta:

```http
GET /result/{task_id}
```

**cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@documento.pdf"
```

**Python:**
```python
import requests

with open('documento.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/upload', files=files)

print(response.json())
```

## 🌐 Swagger UI - Documentación Interactiva

FastAPI genera automáticamente documentación interactiva usando **Swagger UI** y **ReDoc**. Esto permite probar todos los endpoints directamente desde el navegador.

### Acceder a Swagger

Una vez que el servidor esté corriendo:

```
Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
OpenAPI JSON: http://localhost:8000/openapi.json
```

### Usar Swagger para Hacer Requests

#### 1️⃣ Chat Endpoint

1. Abre http://localhost:8000/docs
2. Busca **POST /chat**
3. Haz clic en "Try it out"
4. Completa el formulario:
   ```json
   {
     "user_id": "user123",
     "message": "¿Cuáles son los términos?",
     "database_name": "rappi"
   }
   ```
5. Haz clic en "Execute"
6. Verás la respuesta con el `task_id`

#### 2️⃣ Result Endpoint

1. Copia el `task_id` de la respuesta anterior
2. Busca **GET /result/{task_id}**
3. Haz clic en "Try it out"
4. Pega el `task_id` en el campo
5. Haz clic en "Execute"
6. Verás el estado y resultado

#### 3️⃣ Upload Endpoint

1. Busca **POST /upload**
2. Haz clic en "Try it out"
3. Haz clic en "Choose File"
4. Selecciona un PDF
5. Haz clic en "Execute"
6. El archivo se procesará automáticamente

### Testing desde Swagger

**Ventajas de usar Swagger para testing:**
- ✅ No necesitas cliente externo (cURL, Postman)
- ✅ Generación automática de ejemplos
- ✅ Validación de tipos en tiempo real
- ✅ Historial de requests (en navegador)
- ✅ Interfaz visual amigable

**Flujo de Testing Completo:**

```
1. Abre http://localhost:8000/docs
2. Prueba POST /upload → obtén nombre de BD
3. Prueba POST /chat → obtén task_id
4. Espera unos segundos
5. Prueba GET /result/{task_id} → obtén respuesta
6. Repite con distintas preguntas
```

## 📂 Estructura del Proyecto

```
RAG-semantico-con-FastAPI-Celery-y-Redis/
│
├── main.py                 # API REST - Endpoints principales
├── tasks.py                # Tareas Celery asincrónicas
├── graph.py                # Lógica RAG con LangGraph
├── celery_app.py           # Configuración de Celery
├── config.py               # Variables de configuración
├── memory.py               # Gestión de memoria conversacional
├── paths.py                # Rutas de directorios
├── process_doc.py          # Procesamiento de documentos PDF
├── load_doc.py             # Carga y chunking de documentos
├── vector_store.py         # Gestor de ChromaDB
│
├── requirements.txt        # Dependencias Python
├── .env                    # Variables de entorno (crear)
└── README.md               # Este archivo
```

## 🔧 Descripción de Módulos

### `main.py` - API REST
Define los endpoints HTTP usando FastAPI:
- `POST /chat` - Iniciar procesamiento de pregunta
- `GET /result/{task_id}` - Obtener resultado
- `POST /upload` - Subir nuevo documento

### `tasks.py` - Tareas Asincrónicas
Contiene la tarea Celery `run_llm_graph()`:
- Carga historial de conversación del usuario
- Construye el grafo LangGraph
- Ejecuta la pregunta
- Guarda la conversación actualizada

### `graph.py` - Lógica RAG (LangGraph)

El grafo se compila con `build_graph(vector_store)` y recibe el `VectorStoreManager` ya configurado para la base vectorial de la petición (sin estado global compartido entre tareas).

**Estado (`State`):**

- `messages`: lista de mensajes LangChain (`HumanMessage`, `AIMessage`, …) gestionada con `add_messages`.
- `retrieve_context`: texto devuelto por el retriever de Chroma tras el nodo de contexto.

**Nodos y aristas:**

1. **`context`** (`context_node`): toma el **último** mensaje del usuario (`state["messages"][-1]`), ejecuta `vector_store.retrieve(pregunta)` y guarda el resultado en `retrieve_context`. La búsqueda semántica sigue anclada a la pregunta actual.
2. **`chatbot`** (`chatbot_node`): arma el prompt para el LLM así:
   - Un `SystemMessage` con las instrucciones del sistema (`SYSTEM_INSTRUCTIONS`: asistente de soporte, uso obligatorio del contexto, negativa a inventar si no hay datos, respuesta en español) y el bloque `<contexto_recuperado>...</contexto_recuperado>` con lo almacenado en `retrieve_context`.
   - A continuación concatena **toda** la lista `messages` del estado, de modo que el modelo ve el **historial de conversación** además del contexto RAG.
3. Flujo de ejecución: `START → context → chatbot → END`.

La salida del nodo chatbot devuelve solo el nuevo mensaje del asistente en `messages` (`[response]`), compatible con `add_messages` para no duplicar el historial.

**Resumen:** la recuperación usa la última pregunta; la generación usa **contexto recuperado + historial completo** en una sola invocación al LLM.

### `config.py` - Configuración
Centraliza todas las configuraciones:
- Modelos de OpenAI (embeddings, LLM)
- Parámetros de temperatura
- Conexión a Redis

### `memory.py` - Gestión de Memoria
Persiste conversaciones por usuario:
- Guardar mensajes en histórico
- Cargar histórico para continuar contexto
- Usar Redis como backend

### `paths.py` - Gestión de Rutas
Define las rutas de directorios:
- Uploads: `./uploads`
- Vector stores: `./vector_stores/{db_name}`
- Logs: `./logs`

### `process_doc.py` - Procesamiento de Documentos
Procesa PDFs subidos (ejecutado de forma asíncrona por Celery):
- Recibe `file_path` y `database_name` desde la tarea encolada
- Crea vector store
- Carga embeddings
- Almacena en `./vector_stores`

### `vector_store.py` - Gestor de ChromaDB
Interfaz con la base de datos vectorial:
- Crear colecciones
- Guardar documentos y embeddings
- Recuperar por similitud semántica
- Persistencia en disco

## 💡 Flujo de Ejecución

### Flujo de Chat

```
1. Cliente envía: POST /chat
   {user_id, message, database_name}
   ↓
2. FastAPI recibe y valida request
   ↓
3. Celery encola tarea: run_llm_graph()
   ↓
4. API retorna: {task_id, status: "queued"}
   ↓
5. Cliente recibe task_id
   ↓
6. Celery Worker procesa:
   ├─ Carga historial de usuario (Redis) y lo convierte en mensajes LangGraph
   ├─ Obtiene vector store del documento (`database_name`)
   ├─ Ejecuta el grafo LangGraph:
   │   ├─ Nodo **context**: retrieve con la última pregunta → `retrieve_context`
   │   └─ Nodo **chatbot**: system (instrucciones + contexto RAG) + mensajes del historial → LLM
   ├─ Obtiene respuesta
   └─ Guarda conversación actualizada en Redis
   ↓
7. Resultado almacenado en Redis
   ↓
8. Cliente hace: GET /result/{task_id}
   ↓
9. FastAPI retorna resultado
```

### Flujo de Upload

```
1. Cliente envía: POST /upload (PDF)
   ↓
2. FastAPI guarda archivo en ./uploads
   ↓
3. Encola tarea Celery: process_doc.load_store_doc()
   ↓
4. API retorna: {task_id, status: "queued"}
   ↓
5. Celery Worker toma la tarea y divide PDF en chunks
   ↓
6. Genera embeddings con OpenAI
   ↓
7. Almacena en ChromaDB: ./vector_stores/{nombre_pdf}
   ↓
8. Cliente consulta: GET /result/{task_id}
```

## 🔄 Ejemplo de Uso Completo

### Python Cliente

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Subir documento
print("📄 Subiendo documento...")
with open('documento.pdf', 'rb') as f:
    response = requests.post(f'{BASE_URL}/upload', files={'file': f})
    upload_data = response.json()
    print(upload_data)

upload_task_id = upload_data['task_id']
print(f"Upload Task ID: {upload_task_id}")

# 1.1 Esperar resultado del procesamiento del documento
for _ in range(30):
    upload_result = requests.get(f'{BASE_URL}/result/{upload_task_id}').json()
    if upload_result['result_status'] in ['SUCCESS', 'FAILURE']:
        print("Resultado upload:", upload_result)
        break
    time.sleep(1)

# 2. Hacer pregunta
print("\n❓ Enviando pregunta...")
chat_response = requests.post(f'{BASE_URL}/chat', json={
    'user_id': 'user1',
    'message': '¿Cuál es el contenido principal?',
    'database_name': 'documento.pdf'
})

task_id = chat_response.json()['task_id']
print(f"Task ID: {task_id}")

# 3. Esperar resultado
print("\n⏳ Esperando resultado...")
max_retries = 30
for i in range(max_retries):
    result = requests.get(f'{BASE_URL}/result/{task_id}')
    data = result.json()
    
    if data['result_status'] == 'SUCCESS':
        print(f"\n✅ Respuesta recibida:")
        print(data['result'])
        break
    elif data['result_status'] == 'FAILURE':
        print(f"\n❌ Error: {data['result']}")
        break
    else:
        print(f"Estado: {data['result_status']} - Reintentando en 1s...")
        time.sleep(1)
```

### cURL Script

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. Subir
echo "Uploading document..."
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/upload" \
  -F "file=@documento.pdf"
)
echo "$UPLOAD_RESPONSE"

UPLOAD_TASK_ID=$(echo $UPLOAD_RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)
echo "Upload Task ID: $UPLOAD_TASK_ID"

# 1.1 Esperar resultado de upload
echo "Waiting upload processing..."
for i in {1..30}; do
  UPLOAD_RESULT=$(curl -s "$BASE_URL/result/$UPLOAD_TASK_ID")
  UPLOAD_STATUS=$(echo $UPLOAD_RESULT | grep -o '"result_status":"[^"]*' | cut -d'"' -f4)
  if [ "$UPLOAD_STATUS" = "SUCCESS" ] || [ "$UPLOAD_STATUS" = "FAILURE" ]; then
    echo "$UPLOAD_RESULT"
    break
  fi
  sleep 1
done

# 2. Chat
echo -e "\n\nSending chat request..."
RESPONSE=$(curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user1",
    "message": "¿Cuál es el contenido?",
    "database_name": "documento.pdf"
  }')

TASK_ID=$(echo $RESPONSE | grep -o '"task_id":"[^"]*' | cut -d'"' -f4)
echo "Task ID: $TASK_ID"

# 3. Esperar resultado
echo -e "\nWaiting for result..."
for i in {1..30}; do
  RESULT=$(curl -s "$BASE_URL/result/$TASK_ID")
  STATUS=$(echo $RESULT | grep -o '"result_status":"[^"]*' | cut -d'"' -f4)
  
  if [ "$STATUS" = "SUCCESS" ]; then
    echo "✅ Result:"
    echo $RESULT | grep -o '"result":"[^"]*' | cut -d'"' -f4
    break
  else
    echo "Status: $STATUS - Retrying..."
    sleep 1
  fi
done
```

## 🔧 Recomendaciones para Mejoras y Configuración Avanzada (No Implementadas)

Estas son recomendaciones útiles para mejorar el proyecto, pero **no están implementadas** en el código actual. Se incluyen aquí porque serían beneficiosas para un entorno de producción o desarrollo avanzado.

### Personalizar Swagger UI

Para agregar más información en Swagger, edita `main.py`:

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="RAG API",
    description="Sistema de Preguntas y Respuestas basado en Documentos",
    version="1.0.0",
    docs_url="/docs",           # Ruta de Swagger
    redoc_url="/redoc",         # Ruta de ReDoc
    openapi_url="/openapi.json" # Ruta del esquema OpenAPI
)

# Personalizar OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="RAG API",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

### Documentar Endpoints con Descripciones

Mejora la documentación en Swagger agregando descripciones:

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class ChatRequest(BaseModel):
    """Modelo para solicitudes de chat"""
    user_id: str = Field(..., description="ID único del usuario")
    message: str = Field(..., description="Pregunta del usuario")
    database_name: str = Field(..., description="Nombre de la BD vectorial a usar")

@app.post(
    "/chat",
    summary="Enviar una pregunta",
    description="Envía una pregunta sobre un documento y recibe un task_id para consultar el resultado",
    tags=["Chat"],
    responses={
        202: {"description": "Tarea encolada exitosamente"},
        400: {"description": "Request inválido"}
    }
)
async def chat(request: ChatRequest):
    """
    Procesa una pregunta de forma asincrónica.
    
    **Parámetros:**
    - **user_id**: ID único del usuario para mantener historial
    - **message**: Pregunta a responder sobre el documento
    - **database_name**: Nombre de la BD vectorial (nombre del PDF o ID)
    
    **Retorna:**
    - **task_id**: ID de la tarea para consultar resultado
    - **status**: Estado inicial (siempre "queued")
    """
    pass
```

### Ocultar Endpoints (Opcional)

Si deseas que un endpoint no aparezca en Swagger:

```python
@app.get("/internal", include_in_schema=False)
def internal_endpoint():
    """Este endpoint no aparecerá en Swagger"""
    pass
```

### Exportar Documentación

#### Como JSON

```bash
# Descargar esquema OpenAPI
curl http://localhost:8000/openapi.json > openapi.json
```

#### Como HTML

```bash
# Usar Redocly CLI
npm install -g @redocly/cli

# Generar HTML
redocly build-docs openapi.json
```

### Comparación: Swagger vs Otros

| Característica | Swagger | cURL | Postman | Python |
|---|---|---|---|---|
| **Interfaz** | Web/Gráfica | CLI | GUI Desktop | Código |
| **Documentación** | Automática | Manual | Manual | Manual |
| **Curva Aprendizaje** | Baja | Media | Baja | Media |
| **Instalación** | Incluida | Sistema | Download | pip install |
| **Testing Rápido** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Automatización** | ❌ | ✅ | ✅ | ✅ |

### Tuning de Celery

En `celery_app.py`:

```python
from celery import Celery

app_celery = Celery(
    'worker',
    backend='redis://localhost:6379/5',
    broker='redis://localhost:6379/6',
    include=['tasks', 'process_doc']  # Importante para registrar load_store_doc
)

app_celery.conf.update(
    task_time_limit=600,           # Timeout en segundos
    task_soft_time_limit=550,
    worker_prefetch_multiplier=1,  # Prefetch de tareas
    worker_max_tasks_per_child=100
)
```

### Tuning de ChromaDB

En `vector_store.py`:

```python
VectorStoreManager(
    persist_directory='./vector_stores',
    embedding_model=get_embeddings(),
    collection_metadata={'hnsw:space': 'cosine'}  # o 'l2', 'ip'
)
```

### Cambiar Modelos LLM

En `.env`:

```env
# GPT-4 Turbo (más potente, más caro)
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0

# GPT-3.5 Turbo (económico, rápido)
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.3

# Embeddings alternativos
EMBEDDING_MODEL=text-embedding-3-large
```

### Troubleshooting Avanzado

#### Redis Connection Error
```
Error: ConnectionError: Error 111 connecting to localhost:6379
```

**Solución:**
```bash
# Verificar que Redis está corriendo
redis-cli ping

# O iniciar Redis
redis-server

# O con Docker
docker run -d -p 6379:6379 redis:latest
```

#### Celery Worker No Inicia
```bash
# Verificar que CELERY_BROKER_URL es correcto
echo %CELERY_BROKER_URL%

# O intentar con verbosidad
celery -A celery_app worker --loglevel=debug
```

#### OpenAI API Key Error
```
Error: AuthenticationError: Incorrect API key
```

**Solución:**
- Verificar `.env` tiene `OPENAI_API_KEY` correcto
- Regenerar key en https://platform.openai.com/account/api-keys
- No compartir la key

#### ChromaDB Persistence Error
```bash
# Eliminar cache corrupto
rm -rf ./vector_stores
# O en Windows
rmdir /s /q vector_stores
```

#### Task Timeout
Si las tareas tardan demasiado, aumentar timeout:

```env
# En .env
CELERY_TASK_TIME_LIMIT=900  # 15 minutos
```

#### Puerto 8000 Ya Está en Uso
```bash
# Usar puerto diferente
uvicorn main:app --port 8001
```

### Monitoreo

#### Celery Flower (Dashboard)

```bash
# Instalar
pip install flower

# Ejecutar
celery -A celery_app flower
```

Acceder a: http://localhost:5555

#### Redis CLI

```bash
# Conectar
redis-cli

# Ver keys
KEYS *

# Ver historial de usuario
GET user:user123

# Limpiar todo (⚠️ Cuidado)
FLUSHALL
```

#### Logs Detallados

```bash
# FastAPI con debug
uvicorn main:app --log-level debug

# Celery con debug
celery -A celery_app worker --loglevel=debug
```

## 📈 Mejoras Futuras

- [ ] Autenticación JWT
- [ ] Rate limiting por usuario
- [ ] Webhooks para notificaciones
- [ ] Soporte para más formatos (DOCX, TXT, HTML)
- [ ] Dashboard web de administración
- [ ] Soporte para modelos locales (Ollama, LLaMA)
- [ ] Bases de datos (PostgreSQL) para metadata
- [ ] Búsqueda híbrida (BM25 + Semántica)
- [ ] Versionado de documentos
- [ ] Métricas y analytics

## 📝 Notas Importantes

- **Costos OpenAI**: Monitorear consumo de embeddings y LLM
- **Redis Persistence**: Considerar RDB/AOF si es producción
- **ChromaDB Size**: Considerar migrar a PostgreSQL si es muy grande
- **Seguridad**: Nunca commitar `.env` con API keys
- **Scale**: Para >1000 usuarios, considerar Kubernetes

## 📜 Licencia

Proyecto de código abierto.

## ✉️ Soporte

Para reportar issues o sugerencias, contacta al desarrollador.

---

**Última actualización:** Mayo 2026
**Versión:** 1.0
