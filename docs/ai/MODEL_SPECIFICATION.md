# SIFT Machine Learning Model Strategy & Specification

**Strategy Version:** 1.0  
**Effective Date:** 2026-08-30  
**Scope:** Model Selection, Staged Development, Hybrid Routing, Inference Constraints  

---

## 1. Staged Modeling Roadmap

SIFT adopts a disciplined, empirical staged modeling approach. We explicitly reject jumping directly to ungrounded large language models without established classical benchmarks.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           STAGED ML ARCHITECTURE                             │
│                                                                              │
│  STAGE 1: Classical Baselines                                                │
│  TF-IDF (1-3 ngrams) + Logistic Regression / Linear SVM                      │
│  Establishes fast, reproducible performance floor & feature importance       │
│                                      │                                       │
│                                      ▼                                       │
│  STAGE 2: Domain-Adapted Transformer Fine-Tuning                            │
│  DeBERTa-v3-base / RoBERTa fine-tuned on SIFT JSONL datasets                 │
│  Multi-task heads: Classification (SIF/Precursor) + Span Extraction          │
│                                      │                                       │
│                                      ▼                                       │
│  STAGE 3: Constrained LLM Structured Extraction                              │
│  Instruction-tuned LLM with Pydantic JSON Schema enforcement                 │
│  Specialized for zero-shot entity extraction & grounded rationale synthesis │
│                                      │                                       │
│                                      ▼                                       │
│  STAGE 4: Hybrid Router & Retrieval-Augmented Intelligence (RAG)             │
│  Deterministic Rules + Transformer Classifier + Vector Store (Pinecone)      │
│  Optimal latency, high-SIF recall guarantee, zero-hallucination explainability│
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture per Task

Different tasks have radically different computational and structural requirements:

| Task ID | Task Name | Recommended Architecture | Alternatives Evaluated |
| :--- | :--- | :--- | :--- |
| **TASK-001** | SIF Potential Classification | Fine-tuned DeBERTa-v3 / RoBERTa (Multi-class Cross-Entropy) | TF-IDF + Logistic Regression (Baseline), SetFit Few-Shot |
| **TASK-002** | SIF Precursor Detection | Fine-tuned Transformer Binary Head | Focal Loss Binary Classifier |
| **TASK-003** | Precursor Category Classification | Multi-Label BCEWithLogits Transformer Head | Binary Relevance Classifiers |
| **TASK-004** | Hazard Extraction | Span NER + Taxonomy Mapping Vector Match | Constrained Few-Shot LLM |
| **TASK-005** | Activity Classification | Contextual Classifier Head | Rule-based regex parser |
| **TASK-006** | Life-Saving Rule Mapping | Deterministic Precursor/Hazard Lookup verified by Classifier | Direct categorical head |
| **TASK-007** | Barrier Failure Identification | Span Extraction + Entity Normalization | Catalog-constrained LLM |
| **TASK-008** | Barrier Status Classification | 4-class Sentiment/Polarity Transformer Head | Heuristic keyword matcher |
| **TASK-009** | Evidence Phrase Extraction | Extractive QA Span Head (`start_pos`, `end_pos`) | Token-level BIO Sequence Tagging |
| **TASK-010** | Rationale Generation | Grounded Deterministic Template OR Constrained LLM | N/A |
| **TASK-011** | Urgency Risk Scoring | Transparent Calibrated Heuristic Formula (v1.0) | Multi-attribute Ridge Regression |
| **TASK-012** | Similar Reports Retrieval | Bi-Encoder Dense Embeddings (`all-MiniLM-L6-v2`) in Pinecone | BM25 Lexical Search |
| **TASK-013** | Recurring Pattern Detection | HDBSCAN Dense Vector Clustering + Temporal SQL Grouping | Graph Community Detection |

---

## 3. Recommended Hybrid Production Pipeline

To meet sub-500ms latency budgets and ensure safety-critical recall, the production pipeline utilizes a **Hybrid Router**:

```
                               RAW REPORT NARRATIVE
                                        │
                                        ▼
                                 PREPROCESSING
                             (Sanitization & Tokenization)
                                        │
                        ┌───────────────┴───────────────┐
                        ▼                               ▼
                 DENSE ENCODER                  FAST TRANSFORMER
             (all-MiniLM-L6-v2)               (DeBERTa-v3 SIF Head)
                        │                               │
                        ▼                               ▼
               VECTOR SIMILARITY                 SIF POTENTIAL &
             (Historical Matches)                  PRECURSORS
                        │                               │
                        └───────────────┬───────────────┘
                                        │
                                        ▼
                            EVIDENCE SPAN EXTRACTION
                          (Exact character substring)
                                        │
                                        ▼
                           LIFE-SAVING RULE & BARRIER
                         (Deterministic Catalog Mapping)
                                        │
                                        ▼
                            HEURISTIC URGENCY SCORING
                           (Calculated 0-100 Priority)
                                        │
                                        ▼
                           OUTPUT VALIDATION & SCHEMA
                            (FastAPI Response Contract)
```

---

## 4. Resource & Latency Budgets

| Target Metric | Baseline Model (Stage 1) | Fine-Tuned Transformer (Stage 2) | Production Hybrid (Stage 4) |
| :--- | :--- | :--- | :--- |
| **P95 Latency** | $< 25 \text{ ms}$ | $< 180 \text{ ms}$ (CPU) / $< 30 \text{ ms}$ (GPU) | $< 350 \text{ ms}$ (including vector lookup) |
| **Memory Footprint** | $< 150 \text{ MB}$ RAM | $< 1.2 \text{ GB}$ RAM | $< 2.5 \text{ GB}$ RAM |
| **Model Size** | $< 20 \text{ MB}$ | $\approx 450 \text{ MB}$ (PyTorch / ONNX) | $\approx 600 \text{ MB}$ total |
| **Quantization** | N/A | INT8 / ONNX Runtime | INT8 ONNX Runtime + Pinecone Managed |
