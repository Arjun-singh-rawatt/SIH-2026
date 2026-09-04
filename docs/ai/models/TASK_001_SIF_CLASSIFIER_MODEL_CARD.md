# SIFT Model Card: SIF Potential Classifier (TASK-001 Baseline)

**Model Identifier:** `sift-task-001-baseline`  
**Model Version:** `v0.1.0` (Demo / Baseline Stage 1)  
**Task Modality:** TASK-001 SIF Potential Text Classification  
**Framework:** scikit-learn / joblib / NumPy  
**Authoritative Taxonomy Version:** `1.0`  
**Effective Date:** 2026-08-30  

---

## 1. Model Overview & Architecture

- **Model Type:** Classical Supervised Text Classifier (TF-IDF + Linear Classifier).
- **Primary Function:** Predicts observation severity potential (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NON-SIF`) from unstructured frontline safety narratives.
- **Feature Extraction:** Sublinear TF-IDF word n-grams $(1, 2)$, fitted strictly on the training partition.
- **Algorithms Evaluated:**
  1. Multinomial Logistic Regression (Standard & Balanced Class Weights)
  2. Linear Support Vector Classifier (Standard & Balanced Class Weights)

---

## 2. Intended Use & Scope

### 2.1 Primary Intended Applications:
- Automated initial triage and priority flagging of safety observations across upstream oil & gas operations (drilling, production manifolds, gas compression, pipeline maintenance).
- Establishing a reproducible benchmark floor for future transformer and LLM architectures.

### 2.2 Prohibited Uses:
- **Autonomous Disciplinary Actions:** Predictions must never trigger automated worker sanctions.
- **Autonomous Permit Cancellation:** High-risk flags must route to certified HSE specialists for supervisory verification rather than triggering unreviewed operational shutdowns.
- **Out-of-Domain Usage:** Not intended for downstream petrochemical refining or general commercial building safety without domain adaptation.

---

## 3. Data & Feature Lineage

- **Training Feature:** `raw_text` (unmodified field observation text).
- **Target Label:** `labels.sif_potential` from canonical SIFT DatasetRecord.
- **Feature/Label Separation Invariant:** Post-incident review fields, human reviewer notes, and secondary task labels are strictly excluded from input feature vectors.
- **Temporal Partitioning:** Out-of-time evaluation protocol (70% Train / 15% Validation / 15% Test) with incident event and near-duplicate cluster grouping.

---

## 4. Evaluation Benchmark & Performance Criteria

Per `docs/experiments/EVALUATION_PROTOCOL.md`:

| Metric | Target Specification | Operational Rationale |
| :--- | :--- | :--- |
| **High-SIF Recall ($\text{Recall}_{\text{CRITICAL/HIGH}}$)** | **$\ge 95.0\%$** | Missing high-energy fatal precursors carries catastrophic risk. |
| **Macro F1 Score** | **$\ge 0.88$** | Balances performance across severely imbalanced classes. |
| **P95 Inference Latency** | **$< 25\text{ ms}$** | Sub-second real-time responsiveness during report submission. |

> [!WARNING]
> **DEMO DATASET STATUS:**  
> When evaluated on synthetic demo data (`sift_demo_dataset_v0.1.0`), performance metrics serve strictly to validate pipeline execution. Real statistical performance requires training against certified Oil India Limited ground-truth datasets.

---

## 5. False Negative Diagnostic Protocol

Every model evaluation generates an automated False Negative audit capturing all instances where actual `CRITICAL` or `HIGH` observations were predicted as `MEDIUM`, `LOW`, or `NON-SIF`. Root causes are diagnosed across:
- `INSUFFICIENT_CONTEXT` (narrative under 8 words)
- `CLASS_IMBALANCE_OR_WEAK_WEIGHT` (insufficient penalty for rare high-energy terms)
- `AMBIGUOUS_NARRATIVE` (conflicting housekeeping vs high-energy descriptors)
- `UNKNOWN`

---

## 6. Artifact & Deployment Specifications

- **Serialized Artifact:** `models/task_001/baseline/sift-task-001-baseline-v{VERSION}.joblib`
- **Inference Wrapper:** `ml.task_001.inference.SIFClassifier`
- **Output Schema:** `ml.task_001.schemas.SIFClassificationPrediction`
- **Calibration Status:** Uncalibrated decision scores / probabilities (requires temperature scaling on validation set prior to production serving).
