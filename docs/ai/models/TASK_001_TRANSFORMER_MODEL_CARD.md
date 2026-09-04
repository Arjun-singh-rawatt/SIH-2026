# SIFT Model Card: Pretrained Transformer SIF Classifier (TASK-001)

**Model Identifier:** `sift-task-001-transformer`  
**Model Version:** `v0.1.0`  
**Stage:** Experimental / Pipeline Validation Stage 2  
**Task Modality:** Text Classification (Single-Label Multi-Class)  
**Base Architecture:** DistilBERT (`distilbert-base-uncased`)  
**Parameter Count:** ~66,366,725 parameters  
**Effective Date:** 2026-09-04  
**Release Gate Status:** **DEMO / PIPELINE VALIDATION ONLY**  

---

> [!WARNING]
> **PIPELINE VALIDATION NOTICE:**  
> This model card documents an experimental transformer benchmark evaluated on synthetic demo data (`sift_demo_dataset_v0.1.0`). In accordance with the SIFT Precondition Protocol, **no certified, release-gate-approved human ground-truth dataset currently exists**. Reported metrics confirm pipeline integrity and out-of-time evaluation mechanics; they **MUST NOT be interpreted as real-world operational safety performance**.

---

## 1. Model Overview & Justification

### 1.1 Model Summary
`sift-task-001-transformer` is a fine-tuned transformer encoder tailored for frontline industrial safety narrative screening. It accepts unstructured free-text incident descriptions and maps them into one of five canonical SIF Potential severity levels:
$$\text{SIF Potential} \in \{\text{CRITICAL}, \text{HIGH}, \text{MEDIUM}, \text{LOW}, \text{NON-SIF}\}$$

### 1.2 Architectural Specification
- **Base Encoder:** `distilbert/distilbert-base-uncased` (Sanh et al., 2019).
- **Encoder Depth & Width:** 6 transformer encoder layers, 768 hidden dimensions, 12 self-attention heads, 3,072 intermediate feed-forward dimension.
- **Classification Head:** Linear pooling layer with dropout ($p=0.2$) projecting into 5 logits.
- **Tokenizer:** WordPiece tokenizer (`vocab_size` = 30,522) with canonical lowercase normalization.
- **Max Sequence Length:** 128 subword tokens (covers 100% of frontline safety narratives without truncation).
- **Selection Rationale:** DistilBERT provides 97% of BERT-base's contextual understanding while using 40% fewer parameters and executing 60% faster on inference, making it optimal for edge and CPU/MPS deployment in field hubs.

---

## 2. Intended Use & Operational Scope

### 2.1 Authorized Applications:
- **Triage Priority Ranking:** Automated sorting of incoming daily safety observations to surface suspected high-energy hazards for immediate safety specialist review.
- **Contextual Language Benchmarking:** Serving as a controlled baseline to determine if contextual embeddings outperform n-gram bag-of-words (TF-IDF) on complex industrial phrasing.
- **Assisted Supervisory Screening:** Providing secondary probability scores alongside human HSE inspections.

### 2.2 Strictly Prohibited Applications:
- **Autonomous Disciplinary Actions:** Predictions must never be used to penalize, discipline, or sanction field workers.
- **Autonomous Operational Shutdowns:** Critical predictions must require human verification before triggering unreviewed production halts.
- **Autonomous Permit-to-Work (PTW) Approval:** Cannot be used as the sole gate for issuing high-risk work permits.
- **Out-of-Domain Generalization:** Not calibrated for general office safety, residential construction, or downstream refinery processes without domain adaptation.

---

## 3. Training & Optimization Procedure

- **Loss Objective:** Inverse-frequency class-weighted cross-entropy:
  $$w_c = \frac{N}{K \cdot N_c}$$
  Class weights are fitted strictly on the Training split to counter severe industrial class imbalance.
- **Optimizer:** AdamW ($\beta_1=0.9, \beta_2=0.999, \epsilon=10^{-8}$)
- **Learning Rate:** $2 \times 10^{-5}$ with linear decay
- **Warmup Schedule:** Linear warmup over first 10% of training steps
- **Batch Size:** 8
- **Epochs:** 3
- **Regularization:** Weight decay $0.01$, gradient clipping norm $1.0$
- **Model Checkpoint Selection:** Selected strictly based on the Validation split prioritizing safety-critical recall:
  $$\text{Selection Score} = 0.6 \times \text{High-SIF Recall} + 0.4 \times \text{Macro } F_1$$
- **Locked Test Isolation:** Out-of-time test split was locked during training and evaluated exactly once.

---

## 4. Evaluation Benchmark & Performance Floors

Per `docs/experiments/EVALUATION_PROTOCOL.md`:

| Metric | Target Specification | Operational Rationale |
| :--- | :--- | :--- |
| **High-SIF Recall ($\text{Recall}_{\text{CRITICAL/HIGH}}$)** | **$\ge 95.0\%$** | Failure to detect a fatal precursor carries catastrophic risk. |
| **Macro F1 Score** | **$\ge 0.88$** | Balances performance across severely skewed classes. |
| **Inference Latency (P95)** | **$< 100\text{ ms}$** | Real-time interactive response during incident submission. |

---

## 5. Known Limitations & Failure Modes

1. **Small Demo Dataset Footprint:**  
   Because the released dataset currently contains only demo fixtures, model generalization cannot be guaranteed until training on certified Oil India Limited ground truth datasets.
2. **Confidence Calibration Limitation:**  
   Output probabilities are raw softmax outputs and have not undergone post-hoc calibration (e.g. Temperature Scaling or Isotonic Regression). Softmax values should be treated as heuristic rankings rather than true frequentist probabilities.
3. **Truncation of Multi-Paragraph Incident Inquiries:**  
   Narratives exceeding 128 subword tokens undergo tail truncation. While sufficient for 100% of daily safety observations, formal post-incident investigation reports require document chunking or sliding window pooling.
4. **Passive and Negation Phrasing:**  
   While transformer attention substantially improves over bag-of-words, highly nuanced negative phrasing (e.g., *"isolation was verified before hot work started"* vs *"hot work started before isolation was verified"*) requires continued domain fine-tuning.

---

## 6. Model Artifacts & Reproduction

- **Saved Checkpoint:** `models/task_001/transformer/sift-task-001-transformer-v0.1.0/`
- **Inference Wrapper:** `ml.task_001_transformer.inference.SIFTransformerClassifier`
- **Output Schema:** `ml.task_001.schemas.SIFClassificationPrediction`
- **Evaluation Command:**
  ```bash
  python -m ml.task_001_transformer.evaluate \
      --model-dir models/task_001/transformer/sift-task-001-transformer-v0.1.0 \
      --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl
  ```
