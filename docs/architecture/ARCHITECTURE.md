# SIFT Platform Architecture

**Safety Intelligence & Fatality-risk Tracking Platform**  
High-level architectural blueprint, subsystem boundaries, data contracts, and integration models.

---

## 1. System Topology

```mermaid
graph TD
    Client["React 19 Frontend<br/>(Vite / Tailwind)"] -->|REST JSON API| API["FastAPI Application<br/>(api/app)"]
    
    subgraph "FastAPI Service Layer"
        Router["Routers (api/v1)"]
        Deps["Dependency Injection"]
        Services["Business Services"]
        Repos["SQLAlchemy Repositories"]
        Router --> Deps
        Deps --> Services
        Services --> Repos
    end
    
    subgraph "Data & Storage Tier"
        SQLite["SQLite / PostgreSQL"]
        Vec["Vector Store (Mock / Pinecone)"]
        DataFiles["Data Lake / Split Store<br/>(data/)"]
    end
    
    subgraph "Machine Learning Engine"
        Baseline["Classical Baseline (TF-IDF + LR/SVM)<br/>(ml/task_001)"]
        Transformer["Transformer Classifier (DistilBERT)<br/>(ml/task_001_transformer)"]
        Artifacts["Model Artifacts<br/>(models/task_001/baseline & transformer)"]
    end

    Repos --> SQLite
    Services --> Vec
    Services --> Baseline
    DataFiles --> Baseline
    DataFiles --> Transformer
    Baseline --> Artifacts
    Transformer --> Artifacts
```

---

## 2. Core Subsystems

| Subsystem | Primary Path | Responsibility |
| :--- | :--- | :--- |
| **API** | `api/app/` | Async REST endpoints, Pydantic request/response schemas, service orchestration, database models & repositories. |
| **Frontend** | `src/` | Interactive dashboard, human review triage queue, AI classification insights, action items management, and facility statistics. |
| **Data Pipeline** | `data_pipeline/` | Frontend report ingestion, governance/PII sanitization, deduplication, double-blind annotation batch management, and stratified dataset splitting. |
| **ML Models** | `ml/` | TASK-001 SIF potential classification models: classical linear baseline and fine-tuned contextual transformer. |
| **Model Registry** | `models/` | Serialized model weights: `baseline/` for `.joblib` pipelines and `transformer/` for Hugging Face checkpoints. |
| **Test Suite** | `tests/` & `api/tests/` | Comprehensive test coverage across data pipelines, ML determinism/inference, and FastAPI async endpoints. |
| **Configuration** | `configs/` | Centralized, declarative configuration templates for models and runtime environments. |

---

## 3. Related Architecture Specifications

- [Master AI & Data Specification](SIFT_AI_DATA_SPEC.md)
- [Canonical Safety Taxonomies](../ai/datasets/TAXONOMY.md)
- [Model Specification Roadmap](../ai/models/MODEL_SPECIFICATION.md)
- [Runtime Inference Contract](../ai/models/INFERENCE_CONTRACT.md)
- [Evaluation Protocol](../experiments/EVALUATION_PROTOCOL.md)
