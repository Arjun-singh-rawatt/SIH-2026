# SIFT Experiment Report: `exp-task001-20260830-161115`

**Task:** `TASK-001`  
**Model Type:** `LogisticRegression(class_weight=None, C=1.0)`  
**Dataset Version:** `0.1.0` *(DEMO DATASET - VALIDATION ONLY)*  
**Timestamp:** `2026-08-30T16:11:15.911507+00:00`  
**Random Seed:** `42`

---

> [!WARNING]
> **DEMO DATASET NOTICE:** This model was evaluated against synthetic demo data. Performance numbers verify the pipeline infrastructure and do NOT represent production safety model performance.

## 1. Primary Evaluation Metrics

| Metric | Validation Split | Test Split (Out-of-Time) | Safety Target |
| :--- | :--- | :--- | :--- |
| **High-SIF Recall** | `100.00%` | **`100.00%`** | $\ge 95.0\%$ |
| **Macro F1** | `1.0000` | **`0.3333`** | $\ge 0.88$ |
| **Accuracy** | `100.00%` | `50.00%` | Diagnostic |
| **Weighted F1** | `1.0000` | `0.3333` | Diagnostic |

---

## 2. Test Split Per-Class Breakdown

| SIF Class | Support | Precision | Recall | F1 Score |
| :--- | :--- | :--- | :--- | :--- |
| **CRITICAL** | `1` | `0.5000` | `1.0000` | `0.6667` |
| **NON-SIF** | `1` | `0.0000` | `0.0000` | `0.0000` |

---

## 3. Safety-Critical False Negative Audit

- **Total Test Samples:** `2`

- **Total Misclassifications:** `1`

- **High-SIF False Negatives (Critical/High $\rightarrow$ Low/Non-SIF):** `0`
