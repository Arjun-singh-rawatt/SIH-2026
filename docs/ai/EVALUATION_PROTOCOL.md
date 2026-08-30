# SIFT Machine Learning Evaluation Protocol & Metrics

**Protocol Version:** 1.0  
**Effective Date:** 2026-08-30  
**Scope:** Dataset Splitting, Leakage Prevention, Metric Standards, Error Analysis  

---

## 1. Safety-Critical Metric Priority: SIF-High Recall

In industrial oil and gas operations, **False Negatives on High/Critical SIF reports carry catastrophic operational consequences**. Missing a fatal energy isolation precursor can lead to loss of life, whereas a False Positive merely prompts a 2-minute supervisory review.

Therefore:
$$\text{Primary Operational Objective: } \text{Recall}_{\text{SIF}\in\{\text{CRITICAL}, \text{HIGH}\}} \ge 0.95 \text{ (95\%)}$$
$$\text{Secondary Objective: } \text{Macro } F_1 \ge 0.88$$

---

## 2. Task-by-Task Evaluation Metrics

| Task ID | Task Description | Target Primary Metric | Secondary Supporting Metrics |
| :--- | :--- | :--- | :--- |
| **TASK-001** | SIF Potential Classification | **Recall on CRITICAL/HIGH** ($\ge 95\%$) | Macro $F_1$, Per-class Precision, Confusion Matrix |
| **TASK-002** | SIF Precursor Detection | **Precursor Recall** ($\ge 96\%$) | Binary $F_1$, Specificity |
| **TASK-003** | Precursor Category Classification | **Macro $F_1$** ($\ge 85\%$) | Micro $F_1$, Per-category Recall, Hamming Loss |
| **TASK-004** | Primary Hazard Extraction | **Taxonomy Match Accuracy** ($\ge 90\%$) | Top-3 Accuracy |
| **TASK-005** | Activity Classification | **Macro $F_1$** ($\ge 90\%$) | Overall Accuracy |
| **TASK-006** | Life-Saving Rule Mapping | **Mapping Accuracy** ($\ge 92\%$) | Rule-specific Recall |
| **TASK-007** | Barrier Failure Identification | **Extraction Recall** ($\ge 88\%$) | Exact Match Rate |
| **TASK-008** | Barrier Status Classification | **Macro $F_1$** ($\ge 85\%$) | Multi-class Confusion Matrix |
| **TASK-009** | Evidence Phrase Extraction | **Character Span $F_1$** ($\ge 80\%$) | Exact Match (EM), Token-level Precision/Recall |
| **TASK-010** | Explanation Generation | **Hallucination Rate = 0.0%** | ROUGE-L against Adjudicated Rationale |
| **TASK-011** | Urgency Risk Scoring | **Mean Absolute Error (MAE) $\le 4.5$** | Spearman Rank Correlation ($r_s \ge 0.90$) |
| **TASK-012** | Similar Reports Retrieval | **MRR@10 $\ge 0.85$** | NDCG@10, Precision@5 |
| **TASK-013** | Recurring Pattern Detection | **Silhouette Score $\ge 0.65$** | HSE Specialist Utility Score ($\ge 4.5/5.0$) |

---

## 3. Dataset Splitting & Leakage Prevention Strategy

To ensure genuine generalization and prevent data leakage, datasets must be partitioned using **Temporal Stratified Grouping**:

```
TOTAL ANNOTATED DATASET (100%)
├── 70% TRAIN SPLIT       (Chronologically Older Observations: Months 1 to 8)
├── 15% VALIDATION SPLIT  (Chronologically Intermediate: Months 9 to 10)
└── 15% TEST SPLIT        (Chronologically Latest "Out-of-Time": Months 11 to 12)
```

### Mandatory Leakage Prevention Rules:
1. **Incident Event Grouping:** If multiple safety reports were filed for the same physical incident (e.g. 3 observers logged the same gas leak from different vantage points), all related reports **must reside in the exact same split**.
2. **Near-Duplicate Hashing:** MinHash / Jaccard similarity deduplication is executed prior to splitting. Near-duplicate templates ($\ge 0.85$ similarity) are grouped together.
3. **Out-of-Time Evaluation:** The final test set evaluates future observations against models trained strictly on past data, reflecting real deployment conditions.

---

## 4. Addressing Class Imbalance

Real field datasets typically exhibit severe class imbalance (e.g. `NON-SIF` and `LOW` reports comprise ~70-80% of total volume, while `CRITICAL` represents 5-10%).

### Mandatory Mitigation Strategies:
1. **Cost-Sensitive Class Weighting:** Penalize misclassifying `CRITICAL` / `HIGH` SIF by a factor of $w_c = 4.0\times$ in the loss function:
   $$\mathcal{L}_{\text{weighted}} = -\sum_{c} w_c \cdot y_c \log(\hat{y}_c)$$
2. **Stratified Sampling:** Maintain exact class distribution ratios across train, validation, and test splits.
3. **Rejection of Raw Accuracy:** Accuracy is prohibited as a standalone reporting metric because a naive baseline predicting `NON-SIF` achieves deceptively high accuracy while missing 100% of fatalities.

---

## 5. Mandatory False Negative Root-Cause Analysis

Every model evaluation cycle must generate a **False Negative Audit Report** for all missed `CRITICAL` or `HIGH` SIF observations.

### The 5-Point Root Cause Diagnostic:
1. **Precursor Miss:** Did the model fail to recognize the high-energy hazard mechanism?
2. **Hazard Misinterpretation:** Was technical oilfield terminology (e.g. *accumulator bottle*, *choke manifold*, *Christmas tree*) unrepresented in the vocabulary?
3. **Evidence Span Absence:** Did the model fail to isolate the active failure verb?
4. **Taxonomy Ambiguity:** Was the report narrative borderline between two categories?
5. **Report Narrative Inadequacy:** Was the original text too vague (e.g. *"valve issue noted"*), indicating a need for frontline reporting training?
