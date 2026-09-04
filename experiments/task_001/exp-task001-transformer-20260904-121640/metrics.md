# SIFT Experiment Report: `exp-task001-transformer-20260904-121640`

**Task:** `TASK-001`  
**Model Type:** `Transformer(distilbert-base-uncased)`  
**Dataset Version:** `0.1.0` *(DEMO DATASET - VALIDATION ONLY)*  
**Timestamp:** `2026-09-04T12:16:45.297133+00:00`  
**Random Seed:** `42`

---

> [!WARNING]
> **DEMO DATASET NOTICE:** This model was evaluated against synthetic demo data. Performance numbers verify the pipeline infrastructure and do NOT represent production safety model performance.

## 1. Primary Evaluation Metrics

| Metric | Validation Split | Test Split (Out-of-Time) | Safety Target |
| :--- | :--- | :--- | :--- |
| **High-SIF Recall** | `100.00%` | **`0.00%`** | $\ge 95.0\%$ |
| **Macro F1** | `1.0000` | **`0.0000`** | $\ge 0.88$ |
| **Accuracy** | `100.00%` | `0.00%` | Diagnostic |
| **Weighted F1** | `1.0000` | `0.0000` | Diagnostic |

---

## 2. Test Split Per-Class Breakdown

| SIF Class | Support | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- |
| **CRITICAL** | `0` | `0.0000` | `0.0000` | `0.0000` |
| **HIGH** | `0` | `0.0000` | `0.0000` | `0.0000` |
| **LOW** | `1` | `0.0000` | `0.0000` | `0.0000` |
| **NON-SIF** | `1` | `0.0000` | `0.0000` | `0.0000` |

---

## 3. Safety-Critical False Negative Audit

- **Total Test Samples:** `2`

- **Total Misclassifications:** `2`

- **High-SIF False Negatives (Critical/High $\rightarrow$ Low/Non-SIF):** `0`
