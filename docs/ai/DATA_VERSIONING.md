# SIFT Data & Model Versioning Lifecycle

**Specification Version:** 1.0  
**Effective Date:** 2026-08-30  
**Scope:** Dataset Lineage, Model Cards, Retraining Triggers, Registry Standards  

---

## 1. Dataset Naming & Artifact Lineage

All training, validation, and benchmark datasets must be stored as immutable, version-controlled artifacts following the standardized SIFT naming convention:

`sift_dataset_v{MAJOR}.{MINOR}.{PATCH}_{SPLIT}.jsonl`

### Examples:
- `sift_dataset_v1.0.0_train.jsonl`
- `sift_dataset_v1.0.0_val.jsonl`
- `sift_dataset_v1.0.0_test.jsonl`
- `sift_dataset_v1.0.0_gold_benchmark.jsonl`

### Semantic Versioning Rules for Datasets:
- **MAJOR (v2.0.0):** Breaking changes to the core JSONL schema or removal/redefinition of existing taxonomy classes.
- **MINOR (v1.1.0):** Addition of new annotated observations ($\ge 500$ records) or backwards-compatible taxonomy category additions.
- **PATCH (v1.0.1):** Corrections to typographic errors or span offset adjustments without label changes.

---

## 2. Model Card Standard

Every trained model artifact registered for production or evaluation must accompany a formal **SIFT Model Card** document (`MODEL_CARD.md`):

```markdown
# SIFT Model Card: {model_name}

## 1. Model Overview
- **Model Identifier:** sift-deberta-v3-sif-classifier-v1.2
- **Base Architecture:** DeBERTa-v3-base (86M parameters)
- **Training Dataset:** sift_dataset_v1.2.0_train.jsonl (SHA-256: e3b0c44298fc1c149afbf4c8996fb924...)
- **Taxonomy Version:** 1.0
- **Training Date:** 2026-08-30

## 2. Intended Use & Scope
- **Primary Function:** SIF Potential Classification (TASK-001) & Precursor Detection (TASK-002).
- **Domain:** Upstream oil & gas drilling, gas processing, and pipeline maintenance.
- **Out-of-Scope:** Downstream petrochemical refining or general commercial workplace safety.

## 3. Evaluation Benchmarks (Test Split: sift_dataset_v1.2.0_test.jsonl)
- **SIF-High Recall:** 96.4%
- **Macro F1 Score:** 89.2%
- **Evidence Span Token F1:** 82.1%
- **P95 Latency:** 28 ms (GPU) / 145 ms (CPU ONNX)

## 4. Ethical & Safety Constraints
- **Human Oversight:** Model predictions must never trigger autonomous disciplinary actions; all flags route to certified HSE specialists for validation.
- **False Negative Safeguards:** Review thresholds are biased towards high sensitivity.
```

---

## 3. Continuous Retraining Triggers

Model retraining is not performed on ad-hoc schedules. A formal retraining cycle is triggered upon meeting any of the following operational conditions:

1. **Volume Accumulation:** Over 1,000 newly adjudicated human reviews have been committed to the database.
2. **Performance Degradation (Data Drift):** Human review disagreement rate exceeds 15% over a rolling 30-day window.
3. **New Asset / Basin Commissioning:** Oil India Limited introduces a new operational asset (e.g. deepwater offshore block or new exploration basin) with distinct terminology.
4. **Taxonomy Evolution:** Release of a new taxonomy version (`v1.1` or `v2.0`).
