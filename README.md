# SIFT — Safety Intelligence & Fatality-Risk Tracking Platform

[![React 19](https://img.shields.io/badge/React-19.0.0-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688.svg)](https://fastapi.tiangolo.com)
[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB.svg)](https://www.python.org/)
[![Vite](https://img.shields.io/badge/Vite-6.2.0-646CFF.svg)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4.17-38B2AC.svg)](https://tailwindcss.com/)

**SIFT** (**Safety Intelligence & Fatality-risk Tracking**) is an AI-assisted safety intelligence platform engineered for **Oil India Limited (OIL)**. It transforms unstructured industrial safety observations (Unsafe Acts, Unsafe Conditions, Near Misses, and Incident reports) into structured safety intelligence, classifies SIF (Serious Injury or Fatality) precursors, maps IOGP Life-Saving Rules, diagnoses barrier failure modes, prioritizes CAPA action items, and aggregates executive safety analytics across operational facilities.

---

## 🏛️ Repository Architecture

```text
SIFT/
├── api/                    # FastAPI backend service
│   ├── app/                # Application modules (routes, schemas, services, repos)
│   ├── alembic/            # Database migration scripts
│   └── tests/              # FastAPI endpoint & route-level integration tests
├── configs/                # Centralized declarative configurations
│   ├── task_001/           # ML model hyperparameters (baseline & transformer)
│   └── environments/       # Environment template files
├── data/                   # Data artifacts (annotations, fixtures, metadata, splits)
├── data_pipeline/          # Data ingestion, governance, deduplication, and validation
├── docs/                   # Authoritative documentation suite
│   ├── ai/
│   │   ├── models/         # Model cards, specifications, and baseline runbooks
│   │   ├── datasets/       # Dataset cards, schemas, taxonomies, and guidelines
│   │   └── pipelines/      # Ingestion & double-blind annotation pipelines
│   ├── architecture/       # Master AI & system architecture blueprints
│   ├── development/        # Developer setup, testing, and operational guides
│   └── experiments/        # Benchmark protocols & evaluation metrics
├── experiments/            # Historical experiment runs & benchmark logs
├── ml/                     # ML pipelines & model implementations
│   ├── common/             # Shared loaders, metrics, and error analysis
│   ├── task_001/           # Classical TF-IDF baseline classifier
│   └── task_001_transformer/ # Fine-tuned DistilBERT transformer encoder
├── models/                 # Serialized model weights & tokenizers
│   └── task_001/
│       ├── baseline/       # Serialized .joblib baseline artifacts
│       └── transformer/    # Hugging Face transformer checkpoints
├── scripts/                # Data engineering & pipeline CLI scripts
├── src/                    # Frontend React 19 application (Vite + Tailwind)
├── tests/                  # Root test suite
│   ├── api/                # API router smoke & schema tests
│   ├── data/               # Data pipeline & dataset schema tests
│   ├── ml/                 # ML unit, inference, and determinism tests
│   └── integration/        # End-to-end cross-system integration tests
└── .github/workflows/      # Automated CI/CD pipelines
```

---

## 🚀 Quick Start

### 1. Backend Service

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../configs/environments/development.env.example .env

# Initialize database & seed demo records
python scripts/seed_database.py
alembic upgrade head

# Start FastAPI server (http://localhost:8000)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive API documentation:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 2. Frontend Application

```bash
# From repository root
npm install
npm run dev
```

The React web application is available at [http://localhost:5173](http://localhost:5173).

---

## 🧪 Testing & Validation

```bash
# Run entire test suite (Root tests + API tests)
PYTHONPATH=. api/.venv/bin/pytest

# Run specific test suites
PYTHONPATH=. api/.venv/bin/pytest tests/ml -v
PYTHONPATH=. api/.venv/bin/pytest tests/data -v
PYTHONPATH=. api/.venv/bin/pytest api/tests -v
PYTHONPATH=. api/.venv/bin/pytest tests/integration -v

# Build frontend production bundle
npm run build
```

---

## 📚 Documentation Sitemap

- [Developer Setup & Operations Guide](docs/development/DEVELOPMENT_GUIDE.md)
- [System Architecture Blueprint](docs/architecture/ARCHITECTURE.md)
- [Master AI & Data Specification](docs/architecture/SIFT_AI_DATA_SPEC.md)
- [Frontend to Backend API Integration](API_INTEGRATION.md)
- [Canonical Safety Taxonomies](docs/ai/datasets/TAXONOMY.md)
- [TASK-001 Classical Baseline Runbook](docs/ai/models/TASK_001_BASELINE.md)
- [TASK-001 Pretrained Transformer Benchmark](docs/ai/models/TASK_001_TRANSFORMER.md)
- [Evaluation Protocol & Release Gates](docs/experiments/EVALUATION_PROTOCOL.md)