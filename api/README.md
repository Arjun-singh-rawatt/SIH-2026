# SIFT Backend — Safety Intelligence & Fatality-risk Tracking API

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org)
[![Alembic](https://img.shields.io/badge/Alembic-1.13.0-orange.svg)](https://alembic.sqlalchemy.org)
[![License](https://img.shields.io/badge/License-Proprietary-black.svg)]()

SIFT (**Safety Intelligence & Fatality-risk Tracking**) is an AI-assisted safety intelligence platform engineered for **Oil India Limited (OIL)**. It transforms unstructured industrial safety observations (Unsafe Acts, Unsafe Conditions, Near Misses, and Incident reports) into structured safety intelligence, classifies SIF (Serious Injury or Fatality) precursors, maps IOGP Life-Saving Rules, diagnoses barrier failure modes, prioritizes CAPA action items, and aggregates executive safety analytics across operational facilities.

---

## 🏛️ Architecture Overview

```
Frontend (React 19 / Vite / Tailwind)
               │
               ▼  REST JSON API
┌─────────────────────────────────────────────────────────────┐
│                 SIFT FastAPI Backend (`api/`)               │
├─────────────────────────────────────────────────────────────┤
│  1. FastAPI Routers & Dependency Injection (`app/api/`)     │
│  2. Pydantic v2 Schema Validation (`app/schemas/`)          │
│  3. Business Service Layer (`app/services/`)                │
│     ├── ReportService           ├── ReviewService           │
│     ├── AnalysisService         ├── DashboardService        │
│     ├── IntelligenceService     ├── LifeSavingRuleService   │
│     ├── FacilityService         ├── ActionService           │
│     └── UserService                                         │
├─────────────────────────────────────────────────────────────┤
│  4. Data Access Repositories (`app/db/repositories/`)       │
│     ├── SQLAlchemy 2.0 Async (PostgreSQL / SQLite aiosqlite)│
│     └── Alembic Database Migrations                         │
├─────────────────────────────────────────────────────────────┤
│  5. AI / NLP Protocol Layer (`app/ai/`)                     │
│     ├── AIProvider Interface (Mock / Gemini / HuggingFace)  │
│     └── Domain Rule-based Industrial Safety Classifier      │
├─────────────────────────────────────────────────────────────┤
│  6. Vector Store & Embedding Layer (`app/vector/`)          │
│     ├── VectorStore & EmbeddingProvider Protocols           │
│     └── Mock In-Memory Cosine Store / Pinecone Serverless   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Engineering Principles

1. **Dual Classification Traceability**:
   - Original AI predictions (`ai_sif_potential`, `ai_confidence`, `ai_urgency_score`, `ai_evidence_phrase`) are **never overwritten**.
   - Human reviewer modifications are stored in distinct audit fields (`final_sif_potential`, `reviewer_notes`, `reviewed_at`).
   - Dynamic python properties (`effective_sif_potential`, `effective_life_saving_rule`) provide active operational values.
2. **Deterministic AI & Vector Abstraction**:
   - No hardcoded ML calls in route handlers. AI and Vector engines are abstracted behind Python Protocols (`AIProvider`, `VectorStore`, `EmbeddingProvider`).
3. **Dynamic Precursor Aggregation**:
   - Cross-installation precursor clusters and Life-Saving Rule densities are calculated dynamically from relational database data.
4. **Production-Ready Async Architecture**:
   - Non-blocking I/O using SQLAlchemy AsyncSession, async endpoints, custom exception handlers, and structured logging.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.12+
- `pip` / `virtualenv`

### 2. Environment Setup

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

Default configuration in `.env`:
```ini
APP_NAME=SIFT - Safety Intelligence & Fatality-risk Tracking API
APP_ENV=development
DEBUG=True
PORT=8000
DATABASE_URL=sqlite+aiosqlite:///./sift.db
AI_PROVIDER=mock
VECTOR_STORE_PROVIDER=mock
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]
```

### 4. Database Initialization & Seeding

Run the deterministic database seeder to populate **11 Users**, **10 Facilities**, **52 Safety Reports**, and **32 CAPA Actions**:

```bash
python scripts/seed_database.py
```

Apply Alembic migrations:
```bash
alembic upgrade head
```

### 5. Launch the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation will be available at:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🧪 Running the Test Suite

Run the full pytest suite (12 test modules covering health, reports, AI analysis, human review workflow, dashboard metrics, actions, and vector intelligence):

```bash
pytest tests -v
```

---

## 📡 API Reference Summary

### Health
- `GET /health` — Application health & environment
- `GET /health/db` — Database connectivity & latency check

### Safety Reports
- `GET /api/v1/reports` — Paginated list with multi-attribute filtering (search, facility, type, SIF potential, urgency, rule, status, activity)
- `GET /api/v1/reports/stats` — High-level report counters & SIF exposure density
- `GET /api/v1/reports/{id}` — Full report details (includes facility, barrier assessments, and linked actions)
- `POST /api/v1/reports` — Ingest new safety report (runs AI analysis pipeline)
- `PATCH /api/v1/reports/{id}` — Update report fields
- `DELETE /api/v1/reports/{id}` — Delete report and vector reference
- `GET /api/v1/reports/{id}/actions` — Get action items linked to report

### AI Analysis
- `POST /api/v1/reports/analyze` — Run AI NLP feature extraction on free-text narrative without saving

### Human-in-the-Loop Reviews
- `GET /api/v1/reviews/queue` — Triage queue filtered by tab (`PENDING`, `CRITICAL`, `LOW_CONF`, `ALL`)
- `GET /api/v1/reviews/summary` — Review queue counters
- `POST /api/v1/reports/{id}/review` — Submit HSE review sign-off (`APPROVE`, `MODIFY`, `MARK_NON_SIF`, `ESCALATE`)
- `PATCH /api/v1/reports/{id}/review` — Update review sign-off

### Executive Dashboard
- `GET /api/v1/dashboard/overview` — Executive summary, monthly trends, precursor distribution, facility risk ranking, activity ranking, barrier failures, and priority attention items

### Safety Intelligence & Patterns
- `GET /api/v1/intelligence/overview` — Pattern intelligence KPIs
- `GET /api/v1/intelligence/patterns` — Recurring cross-site precursor clusters
- `GET /api/v1/intelligence/patterns/{id}` — Specific pattern detail and intervention
- `GET /api/v1/intelligence/similar-reports/{id}` — Vector similarity search for historical matches
- `POST /api/v1/intelligence/similar-reports` — Vector similarity search for custom text

### IOGP Life-Saving Rules
- `GET /api/v1/life-saving-rules` — Complete 10 rules with calculated failure metrics
- `GET /api/v1/life-saving-rules/{id}` — Rule details with associated reports

### Facilities
- `GET /api/v1/facilities` — List operational facilities
- `GET /api/v1/facilities/{id}` — Facility details
- `GET /api/v1/facilities/{id}/stats` — Calculated facility safety KPIs

### CAPA Action Items
- `GET /api/v1/actions` — Paginated list with status, priority, and facility filtering
- `GET /api/v1/actions/stats` — Action status counters (Open, In Progress, Completed, Overdue)
- `GET /api/v1/actions/{id}` — Action details
- `POST /api/v1/actions` — Create action item
- `PATCH /api/v1/actions/{id}` — Update action item status / due date
- `DELETE /api/v1/actions/{id}` — Delete action item

### Users
- `GET /api/v1/users` — List active HSE users & investigators
- `GET /api/v1/users/{id}` — User profile
- `POST /api/v1/users` — Register new user

---

## 🐳 Docker Deployment

Build and run the production container:

```bash
docker build -t sift-backend:latest .
docker run -p 8000:8000 --env-file .env sift-backend:latest
```
