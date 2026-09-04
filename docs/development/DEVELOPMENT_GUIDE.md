# SIFT Developer & Operations Guide

Comprehensive guide for local development, environment setup, testing, and repository workflows across the **SIFT** platform.

---

## 1. Repository Structure Overview

```text
SIFT/
├── api/                    # FastAPI backend service
│   ├── app/                # Application modules (routes, schemas, services, repos)
│   ├── alembic/            # Database migration scripts
│   └── tests/              # FastAPI endpoint & route-level integration tests
├── configs/                # Declarative configuration files
│   ├── task_001/           # ML model baseline & transformer training configurations
│   └── environments/       # Environment variable specifications (.env examples)
├── data/                   # Data artifacts (annotations, fixtures, metadata, splits)
├── data_pipeline/          # Ingestion, normalization, governance, validation library
├── docs/                   # Authoritative platform documentation
│   ├── ai/
│   │   ├── models/         # Model cards, specs, and training runbooks
│   │   ├── datasets/       # Dataset cards, schemas, taxonomies, and guidelines
│   │   └── pipelines/      # Ingestion & double-blind annotation pipelines
│   ├── architecture/       # Master system & AI data specifications
│   ├── development/        # Developer setup & operational runbooks
│   └── experiments/        # Evaluation protocols & benchmark procedures
├── experiments/            # Historical experiment runs & model artifacts
├── ml/                     # ML pipelines & model implementations
│   ├── common/             # Shared loaders, metrics, and error analysis
│   ├── task_001/           # Classical TF-IDF baseline classifier
│   └── task_001_transformer/ # Contextual Transformer fine-tuning & evaluation
├── models/                 # Serialized model weights & tokenizers
│   └── task_001/
│       ├── baseline/       # Serialized .joblib baseline artifacts
│       └── transformer/    # Hugging Face transformer weights & tokenizers
├── scripts/                # Utility scripts for data engineering & pipeline runs
├── src/                    # Frontend React 19 application (Vite + Tailwind)
├── tests/                  # Root test suite
│   ├── api/                # API smoke & router tests
│   ├── data/               # Data pipeline & schema unit tests
│   ├── ml/                 # ML unit, inference, and determinism tests
│   └── integration/        # Cross-boundary end-to-end integration tests
└── .github/workflows/      # Automated CI/CD pipelines
```

---

## 2. Environment Setup

### 2.1 Backend (Python 3.12+)

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../configs/environments/development.env.example .env
```

Initialize SQLite database and seed demo fixtures:
```bash
python scripts/seed_database.py
alembic upgrade head
```

Run FastAPI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2.2 Frontend (Node.js 18+)

From repository root:
```bash
npm install
npm run dev
```

The UI is available at `http://localhost:5173`.

---

## 3. Testing & Verification

### 3.1 Running Pytest

Run the entire test suite from the repository root:
```bash
PYTHONPATH=. api/.venv/bin/pytest
```

Run specific test partitions:
```bash
# ML tests only
PYTHONPATH=. api/.venv/bin/pytest tests/ml -v

# Data pipeline tests only
PYTHONPATH=. api/.venv/bin/pytest tests/data -v

# API integration tests
PYTHONPATH=. api/.venv/bin/pytest api/tests -v

# Integration tests
PYTHONPATH=. api/.venv/bin/pytest tests/integration -v
```

### 3.2 Frontend Production Build

```bash
npm run build
```

### 3.3 Static Analysis & Python Compilation

```bash
api/.venv/bin/python -m compileall -q .
npx pyright
```

---

## 4. Machine Learning Workflows

### 4.1 Train Classical Baseline (TASK-001)

```bash
python -m ml.task_001.train \
    --train data/splits/sift_demo_dataset_v0.1.0_train.jsonl \
    --val data/splits/sift_demo_dataset_v0.1.0_val.jsonl \
    --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl \
    --dataset-version 0.1.0 \
    --demo
```

### 4.2 Evaluate Baseline Artifact

```bash
python -m ml.task_001.evaluate \
    --model models/task_001/baseline/sift-task-001-baseline-v0.1.0.joblib \
    --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl
```

### 4.3 Train & Benchmark Transformer (TASK-001)

```bash
python -m ml.task_001_transformer.train \
    --train data/splits/sift_demo_dataset_v0.1.0_train.jsonl \
    --val data/splits/sift_demo_dataset_v0.1.0_val.jsonl \
    --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl \
    --demo
```
