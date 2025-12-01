# 🚀 **S.A.R.A.S — Smart Automated Research Assistant System**

S.A.R.A.S is an end-to-end AI-powered research and content generation system built with:

* **Django Backend (REST APIs)**
* **Custom AI Engine (ManagerAgent + ResearcherAgent + WriterAgent)**
* **RAG Pipeline (PDF ingestion, vector search)**
* **Non-RAG Pipeline (direct generation)**
* **Memory System (Session + Long-Term)**
* **Tools Layer (Google Search, Keyword Extraction, Outline Generation)**
* **Observability (Logging, Tracing, Metrics)**
* **Frontend UI (HTML + Tailwind + JS)**
* **Docker-based Deployment (Dockerfile, docker-compose, Render/GCP)**

S.A.R.A.S is designed to analyze tasks, run multi-step reasoning, gather external information, and generate fully-structured responses with traceability.

---

# 📂 **Project Structure**

```
S.A.R.A.S/
│
├── backend/                     # Full Django backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── saras_backend/           # Django settings and core config
│   ├── core/                    # Base API (health, root, metadata)
│   ├── rag_api/                 # RAG pipeline endpoint
│   ├── non_rag_api/             # Non-RAG agent endpoint
│   ├── trace_api/               # Task trace retrieval
│   ├── memory_api/              # Session + Long-term memory APIs
│   ├── tools_api/               # Available tools list
│   ├── saras_engine_integration/# Bridge between Django & Engine
│   ├── uploads/                 # Uploaded documents for RAG
│   ├── traces/                  # Task execution traces
│   ├── vecstores/               # VectorDB store
│
├── saras_engine/                # ⚙️ Full AI Engine
│   ├── agents/                  # Manager, Researcher, Writer Agents
│   ├── tools/                   # Google Search, Keyword Extractor, Outline Gen
│   ├── memory/                  # Session + Long-term memory
│   ├── observability/           # Logger, Tracer, Metrics
│   ├── evaluation/              # Evaluator & Judge Prompt
│   ├── mcp/                     # MCP Server and Handlers
│
├── frontend/                    # User-facing interface
│   ├── index.html
│   ├── static/
│   │   ├── css/
│   │   └── js/main.js
│
├── deployment/                  # Deployment configurations
│   ├── docker-compose.yml
│   ├── cloud_run_service.yaml
│   ├── render.yaml
│
├── config/                      # Global configs
│   ├── app_config.yaml
│   ├── agent_settings.yaml
│   └── .env.example
│
├── tests/                       # Backend + Engine tests
│
└── README.md
```

---

# ✨ **Key Features**

### 🔮 **1. Multi-Agent AI System**

* **ManagerAgent** → task planning & orchestration
* **ResearcherAgent** → web search + information retrieval
* **WriterAgent** → final structured response generation

### 📄 **2. Full RAG Pipeline**

* PDF ingestion
* Embedding generation
* Vector search
* Evidence collection
* Context-aware response generation

### ⚡ **3. Non-RAG Pipeline**

Fast generation without context or documents.

### 🧠 **4. Memory System**

* **Session memory**: stores conversation history
* **Long-term memory**: persistent knowledge

### 🛠️ **5. Tools Layer**

* Google Search
* Keyword Extraction
* Outline Generation
* Custom tool architecture

### 🔍 **6. Full Observability**

* Logger
* Tracer (step-by-step task trace)
* Metrics

### 🌐 **7. Frontend UI**

Simple, clean UI to upload PDFs, ask questions, and view results.

### 🚢 **8. Easy Deployment**

* Dockerfile
* docker-compose
* Render deployment
* Cloud Run support

---

# 🔧 **Backend API Overview**

## **Health Check**

```
GET /core/health/
```

## **RAG API**

```
POST /rag_api/run/
```

## **Non-RAG API**

```
POST /non_rag_api/run/
```

## **Trace Retrieval**

```
GET /trace_api/<task_id>/
```

## **Memory API**

```
POST /memory_api/session/
POST /memory_api/long_term/
```

## **Tools API**

```
GET /tools_api/list/
```

---

# 🧠 **AI Engine Overview**

### **ManagerAgent**

* Breaks down tasks
* Routes tasks to the correct agent
* Coordinates memory + tools

### **ResearcherAgent**

* Performs Google search
* Extracts keywords
* Retrieves evidence

### **WriterAgent**

* Builds structured, high-quality answers
* Supports markdown output

### **Evaluator**

* Scores responses
* Ensures quality control

---

# ▶️ **Local Development Setup**

## **Backend Setup**

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## **Frontend Setup**

Just open:

```
frontend/index.html
```

## **Engine Setup**

Engine is Python-native; no extra setup required.

---

# 🐳 **Docker Deployment**

### **Using docker-compose**

```bash
cd deployment
docker-compose up --build
```

### **Using Render**

Upload `render.yaml` → Render automatically builds and deploys.

---

# 📦 **Environment Variables**

Copy:

```
cp config/.env.example .env
```

Contains:

```
ENGINE_PATH=
VECTOR_DB_PATH=
GOOGLE_API_KEY=
```

---

# 🧪 **Testing**

Run engine tests:

```bash
pytest tests/engine_tests/
```

Run backend tests:

```bash
pytest tests/backend_tests/
```

---

# 🤝 **Contributing**

* Commit in small atomic steps
* Follow conventional commit messages
* PRs must include clear before/after behavior
* All new code must include comments

---

# 🌟 **License**

MIT License

---

# 🙌 **Author**

**Vinayak Vathare**
Creator of **S.A.R.A.S — Smart Automated Research Assistant System**

---

If you want, I can also generate:
✅ A **high-quality logo**
✅ GitHub **project board**
✅ Issue templates
✅ PR templates

Just tell me!
