# SIFT TASK-001: SIF Potential Classification Baseline

**Task ID:** `TASK-001`  
**Task Modality:** Text Classification (Single-Label Multi-Class)  
**Taxonomy Version:** `1.0`  
**Baseline Model:** TF-IDF + Logistic Regression / Linear SVM  
**Status:** Experimental Baseline (Stage 1 ML Architecture)  
**Applies To:** Safety narrative risk screening floor  

---

## 1. Problem Formulation

Frontline safety observations submitted across drilling rigs, production manifolds, and gas processing plants contain unstructured text narratives describing unsafe behaviors, degraded equipment conditions, and near-miss occurrences.

**TASK-001 predicts the capacity of an observation to generate Serious Injury or Fatality (SIF Potential)**:
$$\text{SIF Potential} \in \{\text{CRITICAL}, \text{HIGH}, \text{MEDIUM}, \text{LOW}, \text{NON-SIF}\}$$

### Safety-Critical Evaluation Floor
In industrial operations, missing a fatal precursor scenario carries catastrophic consequences. Therefore, per `docs/experiments/EVALUATION_PROTOCOL.md`:
$$\text{Primary Operational Metric: } \text{Recall}_{\text{SIF} \in \{\text{CRITICAL}, \text{HIGH}\}} \ge 0.95 \text{ (95.0\%)}$$
$$\text{Secondary Metric: } \text{Macro } F_1 \ge 0.88$$

---

## 2. Feature Engineering & Leakage Isolation

To establish a pure, leakage-free classical baseline:
1. **Input Feature:** `raw_text` (raw unedited field observation narrative).
2. **Feature Representation:** Sublinear Term Frequency - Inverse Document Frequency (`TfidfVectorizer`):
   - Word n-gram range: $(1, 2)$
   - Sublinear TF scaling: $1 + \log(\text{tf})$
   - Normalization: L2 Euclidean norm
   - Stripping: Unicode canonical accents
3. **Data Leakage Invariant:**  
   The vocabulary and IDF weightings are **fitted on the Training partition ONLY** (`fit_transform`). The Validation and Test partitions are projected into the learned vector space via `transform()`, strictly preventing out-of-time vocabulary leakage.
4. **Target & Post-Event Isolation:**  
   No post-event investigation findings, reviewer identities, or ground-truth label fields are passed to the model input space.

---

## 3. Modeling Algorithms & Candidate Architectures

Four candidate configurations are trained and compared across the Validation partition:

| Candidate ID | Model Architecture | Loss / Objective | Class Weighting | Regularization |
| :--- | :--- | :--- | :--- | :--- |
| `lr_standard` | Logistic Regression (L-BFGS) | Multinomial Cross-Entropy | None (`1.0`) | L2 ($C=1.0$) |
| `lr_balanced` | Logistic Regression (L-BFGS) | Multinomial Cross-Entropy | Inversely proportional to frequency | L2 ($C=1.0$) |
| `svm_standard` | Linear Support Vector Classifier | Hinge Loss Margin Maximization | None (`1.0`) | L2 ($C=1.0$) |
| `svm_balanced` | Linear Support Vector Classifier | Hinge Loss Margin Maximization | Inversely proportional to frequency | L2 ($C=1.0$) |

---

## 4. Training & Model Selection Workflow

```
                        TRAIN DATA (70%)
                               │
                               ▼
                    TF-IDF (Fit Vocabulary)
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
        LOGISTIC REGRESSION              LINEAR SVM
        (Standard & Balanced)      (Standard & Balanced)
                │                             │
                └──────────────┬──────────────┘
                               │
                               ▼
                    VALIDATION EVALUATION (15%)
                   (Select Best Macro F1 + Recall)
                               │
                               ▼
                      WINNING BASELINE
                               │
                               ▼
                   FINAL TEST EVALUATION (15%)
                    (Evaluated Exactly Once)
                               │
                               ▼
              EXPERIMENT BUNDLE & JOB_LIB ARTIFACT
```

---

## 5. CLI Execution Reference

### 5.1 Training & Model Selection
```bash
python -m ml.task_001.train \
    --train data/splits/sift_dataset_v1.0.0_train.jsonl \
    --val data/splits/sift_dataset_v1.0.0_val.jsonl \
    --test data/splits/sift_dataset_v1.0.0_test.jsonl \
    --dataset-version 1.0.0 \
    --output-dir experiments/task_001 \
    --model-output models/task_001/baseline \
    --seed 42
```

### 5.2 Standalone Evaluation
Evaluate any serialized `.joblib` model artifact on a test partition without retraining:
```bash
python -m ml.task_001.evaluate \
    --model models/task_001/baseline/sift-task-001-baseline-v1.0.0.joblib \
    --test data/splits/sift_dataset_v1.0.0_test.jsonl \
    --output-dir experiments/task_001/eval_run
```

---

## 6. Python Programmatic Inference

```python
from ml.task_001.inference import SIFClassifier

# Load serialized model pipeline
classifier = SIFClassifier.load("models/task_001/baseline/sift-task-001-baseline-v1.0.0.joblib")

# Single prediction
narrative = "While servicing bypass valve on Compressor #2, noticed 35 bar gas pressure was not isolated."
pred = classifier.predict(narrative)

print(f"Predicted SIF Potential: {pred.predicted_sif_potential}")
print(f"Confidence Score:        {pred.confidence}%")
print(f"Scores Breakdown:        {pred.decision_scores.scores}")
```

---

## 7. Known Limitations & Future Transformer Roadmap

1. **Context Blindness of Bag-of-Words:**  
   TF-IDF n-grams capture local word combinations (e.g. *"without isolation"*, *"wire rope snapped"*), but cannot reason over long-range dependencies or complex passive syntax (e.g. *"isolation was verified by crew before line was unbolted"* vs *"line was unbolted before isolation was verified"*).
2. **Confidence Calibration:**  
   Raw decision scores and uncalibrated softmax probabilities require temperature scaling or isotonic regression on the validation set prior to high-stakes operational deployment.
3. **Stage 2 Transition:**  
   This classical baseline establishes the performance floor. Phase 5 will introduce domain-adapted transformer fine-tuning (`DeBERTa-v3-base`) for simultaneous SIF classification and character evidence span extraction.
