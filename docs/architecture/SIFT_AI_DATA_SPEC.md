# SIFT Master AI & Data Specification

**Document Version:** 1.0  
**Status:** Approved Specification  
**Applies To:** SIFT Backend, Annotation Pipeline, ML Models, Data Contracts  

---

## 1. Problem Formulation

Industrial safety reporting across Oil India Limited (OIL) operations involves thousands of unstructured text observations submitted by frontline operators, drilling engineers, and maintenance contractors. These safety reports fall into four primary categories:
- **Unsafe Act (UA):** Substandard human behavior violating safety protocols.
- **Unsafe Condition (UC):** Physical state of equipment, facility, or environment posing hazards.
- **Near Miss:** An unplanned event that did not result in injury or damage, but had the potential to do so under slightly altered circumstances.
- **Incident:** An unplanned event resulting in actual damage, hydrocarbon release, or injury.

### The Core SIFT Challenge
Conventional safety management often treats all reports with equal weight, resulting in "information overload" where minor housekeeping issues bury critical fatal precursor warnings.

**SIFT transforms unstructured field narratives into structured, prioritized safety intelligence by:**
1. Determining whether the observation involves potential for **Serious Injury or Fatality (SIF)**.
2. Identifying the active **SIF Precursor** mechanism.
3. Categorizing the **Primary Industrial Hazard** and **Operational Activity**.
4. Mapping the observation to standardized **IOGP Life-Saving Rules**.
5. Diagnosing which **Safety Barriers** were failed, weakened, or missing.
6. Extracting exact, traceable **Evidence Phrases** grounding the assessment.
7. Calculating an **Urgency Risk Score** (0–100) to drive rapid intervention.
8. Surfacing cross-site **Recurring Precursor Patterns** and **Semantic Historical Similarities**.

---

## 2. Fundamental AI Task Modalities

To avoid architectural confusion, SIFT formally distinguishes six distinct AI operational modalities:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             SIFT AI MODALITIES                              │
├───────────────────┬─────────────────────────────────────────────────────────┤
│ 1. CLASSIFICATION │ Categorical assignment over discrete label spaces       │
│                   │ (SIF Potential, Precursor Flag, Barrier Status)         │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 2. EXTRACTION     │ Span-level text extraction from raw narrative           │
│                   │ (Evidence Phrases, Hazards, Barrier Mentions)           │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 3. MAPPING        │ Normalization of extracted concepts to controlled       │
│                   │ international standards (IOGP Life-Saving Rules)        │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 4. SCORING        │ Deterministic or regression risk index calculation       │
│                   │ (Urgency Score 0–100, Priority Attention Ranking)       │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 5. RETRIEVAL      │ Semantic dense vector search over historical embeddings  │
│                   │ (Similar Precursor Reports, Prior Investigation Docs)   │
├───────────────────┼─────────────────────────────────────────────────────────┤
│ 6. ANALYTICS      │ Cross-facility aggregation & cluster pattern detection   │
│                   │ (Precursor Density, SIF Frequency, Barrier Weaknesses)  │
└───────────────────┴─────────────────────────────────────────────────────────┘
```

---

## 3. Formal Task Registry (TASK-001 through TASK-013)

### TASK-001: SIF Potential Classification
- **Objective:** Classify the severity capacity of the observation into a canonical potential tier.
- **Input:** Raw report narrative (`text`), report type, operational context.
- **Output:** Categorical label (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `NON-SIF`).
- **Task Type:** Multi-class single-label classification.
- **Required Labels:** SIF Potential Tier (`SIFPotentialLevel`).
- **Annotation Required:** Yes (Double-blind + Adjudication).
- **ML Formulation:** Supervised Transformer / Linear Baseline / LLM Structured output.
- **Evaluation Metrics:** Macro F1, High-SIF Recall (Target ≥ 95%), Precision, Confusion Matrix.
- **Dependencies:** None.

---

### TASK-002: SIF Precursor Detection
- **Objective:** Determine if a high-energy hazard was present in the absence of a direct, functioning barrier.
- **Input:** Raw report narrative (`text`).
- **Output:** `YES`, `NO`, or `POTENTIAL`.
- **Task Type:** Multi-class classification.
- **Required Labels:** Precursor Flag (`SIFPrecursorFlag`).
- **Annotation Required:** Yes.
- **ML Formulation:** Supervised Binary/Multi-class classifier.
- **Evaluation Metrics:** Binary/Macro F1, Precision, Recall.
- **Dependencies:** None.

---

### TASK-003: Precursor Category Classification
- **Objective:** Identify the physical mechanism and high-energy source driving the precursor risk.
- **Input:** Raw report narrative (`text`), operational context.
- **Output:** Primary precursor category and optional secondary categories (e.g. Primary: `Energy Isolation`, Secondary: `[Confined Space]`).
- **Task Type:** Multi-label classification.
- **Required Labels:** Controlled Precursor Categories (`PrecursorCategory`).
- **Annotation Required:** Yes.
- **ML Formulation:** Multi-label Supervised Classifier / LLM JSON schema.
- **Evaluation Metrics:** Micro F1, Macro F1, Per-category Recall, Hamming Loss.
- **Dependencies:** TASK-002 (`sif_precursor == YES`).

---

### TASK-004: Primary Hazard Extraction & Normalization
- **Objective:** Extract and normalize the primary physical, chemical, or environmental hazard.
- **Input:** Raw report narrative (`text`).
- **Output:** Canonical hazard string from controlled taxonomy (e.g. `Stored / Pressurized Hydrocarbon Energy`).
- **Task Type:** Extraction + Taxonomy Normalization.
- **Required Labels:** `PrimaryHazardType`.
- **Annotation Required:** Yes.
- **ML Formulation:** Named Entity Recognition (NER) / Few-shot extraction mapped to taxonomy.
- **Evaluation Metrics:** Top-1 Accuracy, Exact Match, Taxonomy Compliance Rate.
- **Dependencies:** None.

---

### TASK-005: Activity Extraction & Classification
- **Objective:** Identify the operational activity underway when the observation occurred.
- **Input:** Raw report narrative (`text`), metadata context.
- **Output:** Activity category (e.g. `Maintenance`, `Drilling Operations`, `Vessel Cleaning`).
- **Task Type:** Single-label classification.
- **Required Labels:** `ActivityCategory`.
- **Annotation Required:** Yes.
- **ML Formulation:** Supervised Classifier / Rule-assisted contextual parser.
- **Evaluation Metrics:** Macro F1, Accuracy.
- **Dependencies:** None.

---

### TASK-006: IOGP Life-Saving Rule Mapping
- **Objective:** Map the event to the standardized IOGP Life-Saving Rule designed to prevent the fatality.
- **Input:** Raw report text, extracted hazard, detected precursor.
- **Output:** Controlled Rule Identifier (e.g. `Energy Isolation`, `Confined Space Entry`).
- **Task Type:** Categorical Mapping / Classification.
- **Required Labels:** `LifeSavingRuleIdentifier`.
- **Annotation Required:** Yes.
- **ML Formulation:** Deterministic mapping table verified by model classifier.
- **Evaluation Metrics:** Mapping Accuracy, Macro F1.
- **Dependencies:** TASK-003 (Precursor), TASK-004 (Hazard).

---

### TASK-007: Barrier Failure Identification
- **Objective:** Identify the specific engineered, administrative, or behavioral safety barrier that failed or degraded.
- **Input:** Raw report narrative (`text`), detected Life-Saving Rule.
- **Output:** Standardized barrier name (e.g. `Zero Energy Verification & Isolation Certificate`).
- **Task Type:** Structured Entity Extraction.
- **Required Labels:** Barrier Name string from barrier catalog.
- **Annotation Required:** Yes.
- **ML Formulation:** Extraction + Catalog alignment.
- **Evaluation Metrics:** Precision, Recall, Taxonomy validity.
- **Dependencies:** TASK-004, TASK-006.

---

### TASK-008: Barrier Status Classification
- **Objective:** Classify the operational integrity of the diagnosed barrier.
- **Input:** Barrier text mention + narrative context.
- **Output:** `FAILED`, `WEAK`, `EFFECTIVE`, `UNKNOWN`.
- **Task Type:** Multi-class classification.
- **Required Labels:** `BarrierStatusLevel`.
- **Annotation Required:** Yes.
- **ML Formulation:** Contextual sentiment / status classifier.
- **Evaluation Metrics:** Macro F1, Per-status Confusion Matrix.
- **Dependencies:** TASK-007.

---

### TASK-009: Grounded Evidence Phrase Extraction
- **Objective:** Extract the exact, unedited text span from the report narrative directly justifying the SIF classification.
- **Input:** Raw report narrative (`text`).
- **Output:** List of spans with `text`, `start_offset`, `end_offset`.
- **Task Type:** Span Extraction / Question Answering.
- **Required Labels:** List of Character-offset Grounded Spans.
- **Annotation Required:** Yes.
- **ML Formulation:** Span Extraction (e.g. Question Answering head / Extractive Summarization).
- **Evaluation Metrics:** Character Span F1, Token-level Precision/Recall, Exact Match.
- **Dependencies:** TASK-001.

---

### TASK-010: AI Explanation Generation
- **Objective:** Synthesize a concise, transparent 1–2 sentence rationale grounded strictly in the report's facts.
- **Input:** Extracted entities (Precursor, Hazard, Barrier, Evidence, Consequence).
- **Output:** Structured natural language explanation string.
- **Task Type:** Natural Language Generation (Grounded Template or LLM).
- **Required Labels:** Gold standard human review rationale.
- **Annotation Required:** Optional (Evaluated for hallucination-free factual grounding).
- **ML Formulation:** Deterministic Template Assembly OR Constrained LLM generation.
- **Evaluation Metrics:** Hallucination Rate (0%), Faithfulness, ROUGE-L against expert notes.
- **Dependencies:** TASK-001 through TASK-009.

---

### TASK-011: Urgency Risk Index Scoring
- **Objective:** Compute a standardized 0–100 integer score reflecting immediate HSE triage priority.
- **Input:** SIF Potential, Hazard Severity, Barrier Status, Activity Risk, Consequence.
- **Output:** Integer score `0–100` and `UrgencyScoreBreakdown`.
- **Task Type:** Transparent Scoring Heuristic / Calibrated Risk Function.
- **Required Labels:** Urgency score integer.
- **Annotation Required:** Calibrated against expert triage ranking.
- **ML Formulation:** Baseline Weighted Scoring Function (Versioned Heuristic).
- **Evaluation Metrics:** Mean Absolute Error (MAE), Spearman Rank Correlation against HSE manager priority ranking.
- **Dependencies:** TASK-001, TASK-004, TASK-008.

---

### TASK-012: Historical Semantic Similarity Retrieval
- **Objective:** Retrieve top-K historical reports exhibiting identical hazard mechanics or barrier failure modes.
- **Input:** Query text embedding OR Report ID vector.
- **Output:** Ranked list of similar historical reports with cosine similarity scores.
- **Task Type:** Dense Vector Semantic Retrieval.
- **Required Labels:** Implicit (Cosine distance over dense embeddings).
- **Annotation Required:** No (Validated via relevance judgment benchmarks).
- **ML Formulation:** Dense Embeddings (e.g. `all-MiniLM-L6-v2` / `text-embedding-3-small`) in Pinecone / Local Index.
- **Evaluation Metrics:** Mean Reciprocal Rank (MRR@10), Precision@5, NDCG@10.
- **Dependencies:** None.

---

### TASK-013: Recurring Precursor Pattern Detection
- **Objective:** Aggregate multi-site safety observations to detect emerging clusters of systemic barrier failure.
- **Input:** Database of classified reports over a sliding temporal window (30D, 90D, 1Y).
- **Output:** Pattern clusters with occurrence counts, affected facilities, dominant barrier failures, and recommended interventions.
- **Task Type:** Unsupervised Graph Clustering / Dimensional Analytics.
- **Required Labels:** Systemic cluster identifiers.
- **Annotation Required:** Subject-matter expert validation of generated pattern insights.
- **ML Formulation:** Density-based Clustering (HDBSCAN) + SQL Grouping Analytics.
- **Evaluation Metrics:** Cluster Silhouette Score, HSE Interventional Utility Rating.
- **Dependencies:** TASK-001, TASK-003, TASK-007, TASK-008.

---

## 4. Summary Matrix of AI Tasks

| Task ID | Task Name | Modality | Output Type | Primary Evaluation Metric |
| :--- | :--- | :--- | :--- | :--- |
| **TASK-001** | SIF Potential Classification | Classification | Single-Label (5 classes) | Macro F1 & High-SIF Recall |
| **TASK-002** | SIF Precursor Detection | Classification | Single-Label (3 classes) | Binary / Macro F1 |
| **TASK-003** | Precursor Categorization | Classification | Multi-Label (12 classes) | Micro & Macro F1 |
| **TASK-004** | Primary Hazard Extraction | Extraction | Controlled String | Top-1 Accuracy |
| **TASK-005** | Activity Classification | Classification | Single-Label (12 classes) | Macro F1 |
| **TASK-006** | Life-Saving Rule Mapping | Mapping | Controlled String | Mapping Accuracy |
| **TASK-007** | Barrier Failure Diagnosis | Extraction | Controlled String | Extraction Recall |
| **TASK-008** | Barrier Status Classification| Classification | Single-Label (4 classes) | Macro F1 |
| **TASK-009** | Evidence Phrase Extraction | Extraction | Spans with Offsets | Span-level Token F1 |
| **TASK-010** | Explanation Generation | Generation | Grounded Sentence | Faithfulness & Zero Hallucination |
| **TASK-011** | Urgency Risk Scoring | Scoring | Integer `0–100` | MAE & Rank Correlation |
| **TASK-012** | Similar Reports Retrieval | Retrieval | Ranked Matches + Score | MRR@10 & NDCG@10 |
| **TASK-013** | Recurring Pattern Detection | Analytics | Clusters & Interventions | Cluster Silhouette Score |

---

## 5. End-to-End Pipeline Architecture

```
                                  FIELD SAFETY REPORT
                              (UA / UC / Near Miss / Incident)
                                             │
                                             ▼
                                  PREPROCESSING & SANITIZATION
                                             │
                                             ▼
                                DENSE VECTOR EMBEDDING
                              (For Similarity & Retrieval)
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       │                                           │
                       ▼                                           ▼
              TASK-001 & TASK-002                         TASK-004 & TASK-005
           SIF POTENTIAL & PRECURSOR                     HAZARD & ACTIVITY EXTRACTION
                       │                                           │
                       └─────────────────────┬─────────────────────┘
                                             │
                                             ▼
                                    TASK-003 & TASK-006
                               PRECURSOR & LIFE-SAVING RULE
                                             │
                                             ▼
                                    TASK-007 & TASK-008
                                BARRIER FAILURE & STATUS
                                             │
                                             ▼
                                    TASK-009 & TASK-010
                              EVIDENCE EXTRACTION & RATIONALE
                                             │
                                             ▼
                                         TASK-011
                                   URGENCY SCORE INDEX
                                             │
                                             ▼
                                    STRUCTURED RESULT
                                             │
                       ┌─────────────────────┴─────────────────────┐
                       ▼                                           ▼
             PERSISTENCE & AUDIT                            VECTOR INDEX
           PostgreSQL (SafetyReport)                     Pinecone / Local Index
                       │
                       ▼
             HUMAN-IN-THE-LOOP REVIEW
             (Approved / Modified Sign-off)
```
