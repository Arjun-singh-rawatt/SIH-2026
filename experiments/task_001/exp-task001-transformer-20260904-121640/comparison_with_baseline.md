# SIFT TASK-001 Benchmark Comparison: Classical Baseline vs Transformer

**Dataset Version:** `0.1.0` *(DEMO / PIPELINE VALIDATION ONLY)*  
**Test Sample Count:** `2` (Evaluated on identical locked test set)

> [!WARNING]
> **DEMO DATASET NOTICE:** Evaluated against synthetic demo data. Numbers demonstrate end-to-end pipeline integrity and do NOT represent production statistical performance.

## 1. Head-to-Head Performance Summary

| Model Architecture | Accuracy | Macro F1 | HIGH-SIF Recall | Parameter Count |
| :--- | :--- | :--- | :--- | :--- |
| **Classical (LogisticRegression(class_weight=None, C=1.0))** | `0.00%` | `0.0000` | **`0.00%`** | ~N-Gram Vocab |
| **Transformer (distilbert-base-uncased)** | `0.00%` | `0.0000` | **`0.00%`** | ~66.36M |

---

## 2. Comparative Prediction Overlap Matrix

| Category | Record Count | Percentage | Operational Interpretation |
| :--- | :--- | :--- | :--- |
| **Both Correct** | `0` | `0.0%` | High agreement across salient hazard vocabulary. |
| **Transformer Only** | `0` | `0.0%` | Contextual syntax / passive phrasing captured. |
| **Classical Only** | `0` | `0.0%` | Direct keyword match prioritized over subtle context. |
| **Both Wrong** | `2` | `100.0%` | High ambiguity, missing context, or rare hazard terminology. |

---

## 3. Sample-Level Case Comparisons

| Report ID | Actual Label | Classical Pred | Transformer Pred | Category | Narrative Excerpt |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SIF-2026-00004` | `NON-SIF` | `CRITICAL` | `HIGH` | `BOTH_WRONG` | During routine housekeeping in workshop, empty cardboard boxes were found stacked near the emergency exit corridor. Clea... |
| `SIF-2026-00005` | `LOW` | `CRITICAL` | `CRITICAL` | `BOTH_WRONG` | Mechanic technician suffered minor skin abrasion while tightening grease nipple on pump skid. Cleaned and dressed at Fir... |