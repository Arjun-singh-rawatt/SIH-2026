# SIFT TASK-001: Pretrained Transformer Benchmark Documentation

**Task ID:** `TASK-001`  
**Task Title:** SIF Potential Classification  
**Modality:** Pretrained Transformer Encoder with Sequence Classification Head  
**Stage:** Stage 2 Benchmark (Contextual Language Representation Floor)  
**Taxonomy Version:** `1.0`  
**Release Gate Status:** **DEMO / PIPELINE VALIDATION ONLY**  

---

> [!WARNING]
> **PRECONDITION PROTOCOL COMPLIANCE (DEMO NOTICE):**  
> An audit of the dataset registry and SQLite database confirmed that only synthetic demo fixtures (`sift_demo_dataset_v0.1.0`) are currently available. No human double-blind ground-truth release has cleared the dataset release gates. Therefore, all metrics and results in this report serve exclusively to validate pipeline execution, out-of-time evaluation isolation, and serialization mechanics. **They MUST NOT be construed as real-world operational performance.**

---

## 1. Motivation & Problem Formulation

Frontline safety observations in oil and gas operations frequently describe complex hazards using passive voice, jargon, and implicit severity indicators. 

The Stage 1 classical baseline (`TF-IDF + Logistic Regression / Linear SVM`) operates on bag-of-words n-grams. While computationally efficient, TF-IDF cannot differentiate phrasing context where word order reverses safety meaning:
- *"PTW issued before line was opened"* (Safe procedure followed)  
  vs  
- *"Line was opened before PTW was issued"* (Severe SIF precursor breach)

The **TASK-001 Transformer Benchmark** determines whether bidirectional contextual language representations (`DistilBERT`) capture these semantic nuances and improve SIF Potential classification over classical baselines:
$$\text{SIF Potential} \in \{\text{CRITICAL}, \text{HIGH}, \text{MEDIUM}, \text{LOW}, \text{NON-SIF}\}$$

---

## 2. Model Architecture & Selection Justification

### 2.1 Model Specification
| Attribute | Specification |
| :--- | :--- |
| **Base Model Architecture** | DistilBERT (`distilbert-base-uncased`) |
| **Pretrained Source** | Hugging Face Hub (`distilbert/distilbert-base-uncased`) |
| **Total Parameters** | ~66,366,725 parameters |
| **Encoder Depth** | 6 transformer layers |
| **Hidden Dimension ($d_{\text{model}}$)** | 768 |
| **Self-Attention Heads** | 12 heads |
| **Tokenizer** | WordPiece (`vocab_size` = 30,522) |
| **Classification Head** | Dense pooling layer ($768 \rightarrow 768$) + Dropout ($p=0.2$) + Linear ($768 \rightarrow 5$) |
| **Max Sequence Length** | 128 subword tokens |

### 2.2 Architectural Justification
DistilBERT was selected as the primary candidate encoder for this benchmark because:
1. **Lightweight Footprint:** 40% fewer parameters than BERT-base (66M vs 110M), reducing memory pressure and training latency.
2. **Knowledge Retention:** Retains 97% of BERT-base's contextual language understanding capabilities.
3. **Execution Safety:** Runs reliably on both Apple Silicon MPS and standard CPU environments without Out-Of-Memory (OOM) risks.
4. **Configurability:** The architecture is decoupled via `--base-model`, permitting seamless future benchmarks with RoBERTa or DeBERTa-v3.

---

## 3. Dataset & Tokenization Analysis

### 3.1 Dataset Splits & Leakage Prevention
The benchmark consumes the canonical SIFT release (`data/splits/sift_demo_dataset_v0.1.0`):
- **TRAIN Split:** Model parameter fine-tuning.
- **VALIDATION Split:** Epoch checkpoint selection and early stopping.
- **TEST Split:** Locked out-of-time evaluation partition, evaluated strictly ONCE.

Target leakage is prevented by:
- Input feature is strictly `raw_text`.
- Reviewer notes, final adjudicated labels, AI explanations, and post-event investigations are completely excluded from inputs.

### 3.2 Narrative Length Distribution Audit
Before fixing the sequence window, an empirical audit across all available safety narratives was conducted:

| Quantile | Character Count | Word Count | Subword Token Count | Truncation Impact |
| :--- | :--- | :--- | :--- | :--- |
| **Min** | 30 | 5 | 7 | 0% |
| **Median** | 114 | 17.5 | 22 | 0% |
| **75th Percentile** | 150 | 20.0 | 26 | 0% |
| **90th Percentile** | 198.5 | 27.9 | 36 | 0% |
| **95th Percentile** | 284 | 45.0 | 58 | 0% |
| **Max** | 284 | 45.0 | 58 | 0% |

**Handling Long Narratives:**  
With `max_length = 128`, **0% of frontline observations undergo truncation**. For future formal investigation reports that may exceed 512 tokens, a chunking or sliding-window pooling strategy is documented for Phase 5.

---

## 4. Class Imbalance Mitigation

The training split exhibits heavy skew towards high-energy precursors in upstream drilling. To mitigate class dominance, inverse-frequency class weighting is applied to the Cross-Entropy loss:
$$w_c = \frac{N}{K \cdot N_c}$$

Class weights are derived **strictly from the training split**:
- `CRITICAL`: 0.75
- `HIGH`: 1.50
- `MEDIUM`: 1.00 (neutral for unobserved classes)
- `LOW`: 1.00
- `NON-SIF`: 1.00

---

## 5. Training Configuration & Early Stopping

| Hyperparameter | Value | Description |
| :--- | :--- | :--- |
| `learning_rate` | $2 \times 10^{-5}$ | AdamW initial learning rate |
| `batch_size` | 8 | Batch size for train and validation |
| `epochs` | 3 | Full training passes |
| `weight_decay` | 0.01 | L2 regularization parameter |
| `warmup_ratio` | 0.10 | Linear warmup over first 10% steps |
| `seed` | 42 | Deterministic seed across NumPy, PyTorch |
| `device` | `auto` | Auto-detects MPS $\rightarrow$ CUDA $\rightarrow$ CPU |

### Checkpoint Selection Policy
Model selection occurs strictly on the Validation split:
$$\text{Selection Score} = 0.6 \times \text{High-SIF Recall} + 0.4 \times \text{Macro } F_1$$
The locked test partition is evaluated exactly once using the best validation checkpoint.

---

## 6. Execution Commands & Reproducibility

### 6.1 Training & Model Selection CLI
```bash
PYTHONPATH=. python -m ml.task_001_transformer.train \
    --train data/splits/sift_demo_dataset_v0.1.0_train.jsonl \
    --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl \
    --base-model distilbert-base-uncased \
    --dataset-version 0.1.0 \
    --epochs 3 \
    --batch-size 8 \
    --learning-rate 2e-5 \
    --max-length 128 \
    --output-dir experiments/task_001 \
    --model-output models/task_001/transformer \
    --seed 42 \
    --demo
```

### 6.2 Standalone Evaluation CLI
```bash
PYTHONPATH=. python -m ml.task_001_transformer.evaluate \
    --model-dir models/task_001/transformer/sift-task-001-transformer-v0.1.0 \
    --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl \
    --output-dir experiments/task_001/eval_run
```

### 6.3 Programmatic Inference API
```python
from ml.task_001_transformer.inference import SIFTransformerClassifier

classifier = SIFTransformerClassifier.load(
    "models/task_001/transformer/sift-task-001-transformer-v0.1.0"
)
pred = classifier.predict(
    "While servicing bypass valve on Compressor #2, noticed 35 bar gas pressure was not isolated."
)
print("Predicted SIF Potential:", pred.predicted_sif_potential)
print("Confidence:", pred.confidence, "%")
print("Class Probabilities:", pred.decision_scores.scores)
```

---

## 7. Known Limitations & Future Roadmap

1. **Synthetic Data Precondition:**  
   Because genuine Oil India Limited ground-truth datasets are pending release adjudication, results do not establish real-world statistical superiority.
2. **Confidence Calibration:**  
   Probabilities are uncalibrated softmax values. Temperature scaling on validation data is recommended before high-stakes automated routing.
3. **Multi-Task Horizon (TASK-002 & Span Extraction):**  
   Future iterations will explore joint multi-task heads for simultaneous SIF potential classification, precursor category multi-labeling, and character-offset evidence span extraction (`DeBERTa-v3-base`).
