# SIFT Dataset Card: SIFT Canonical Safety Intelligence Dataset

**Dataset Name:** SIFT Safety Intelligence & Fatality-Risk Tracking Dataset  
**Canonical Identifier:** `sift_dataset`  
**Current Taxonomy Version:** `1.0`  
**Schema Version:** `1.0`  
**Effective Date:** 2026-08-30  
**License / Data Access:** Proprietary — Oil India Limited (OIL) HSE Operations  

---

## 1. Dataset Overview & Purpose

The SIFT dataset comprises structured, validated safety observations collected across upstream exploration, drilling, gas processing, pipeline transportation, and central maintenance complexes. Its primary objective is to train, benchmark, and evaluate machine learning models capable of identifying high-energy hazards and Serious Injury or Fatality (SIF) precursors buried within frontline safety narratives.

---

## 2. Intended Use & Scope

### 2.1 Primary Intended Applications:
- **SIF Potential Classification (TASK-001):** Classifying observation capacity into `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or `NON-SIF`.
- **SIF Precursor Detection (TASK-002 & TASK-003):** Detecting high-energy hazard exposure pathways and multi-label precursor mechanisms.
- **Hazard & Activity Categorization (TASK-004 & TASK-005):** Extracting physical hazards and operational context.
- **IOGP Life-Saving Rule Mapping (TASK-006):** Mapping events to international safety standards.
- **Safety Barrier Integrity Diagnosis (TASK-007 & TASK-008):** Identifying failed, weakened, or missing physical/administrative barriers.
- **Grounded Evidence Phrase Extraction (TASK-009):** Extracting exact character substrings supporting classifications.

### 2.2 Prohibited Uses:
- **Autonomous Disciplinary Actions:** Under no circumstances may dataset labels or model predictions be used for automated punitive or disciplinary action against workers.
- **Out-of-Domain Generalization:** The dataset reflects upstream oil and gas operations and must not be applied directly to medical, nuclear, or aviation safety without domain adaptation.
- **Unverified Retraining:** Un-adjudicated or single-annotator data must not be ingested into production training sets.

---

## 3. Data Collection, Provenance & Classification

All acquired sources are registered in `data/metadata/source_registry.json` under four strict classifications:
1. **`REAL`**: Authentic frontline reports from OIL operating fields.
2. **`PUBLIC`**: Open-access regulatory datasets (OSHA, CSB).
3. **`SYNTHETIC`**: Algorithmic test fixtures for automated regression testing.
4. **`DEMO`**: Seeded IDE preview records (**never used as ML ground truth**).

### Granular Lineage Tracking:
Every record tracks `source_id`, `source_record_id`, `source_file`, and `ingestion_timestamp`.

---

## 4. Annotation Protocol & Quality Assurance

- **Double-Blind Independent Annotation:** To eliminate cognitive bias, human HSE specialists annotate raw reports without exposure to model predictions (`ai_*`), historical confidence, or prior reviewer notes.
- **Multi-Faceted Agreement Auditing:** Paired annotations are audited using Cohen's Kappa ($\kappa$) for categorical labels, Jaccard set similarity for multi-label precursors and barriers, and character-level IoU for evidence spans.
- **Lead Specialist Adjudication:** Records with conflicting labels are flagged (`ADJUDICATION_REQUIRED`) and resolved by a certified Lead HSE Adjudicator.
- **Evidence Offset Invariant:** All extracted evidence phrases are validated character-for-character against raw text: `raw_text[start_offset:end_offset] == text`.

---

## 5. Pre-Flight Release Gate Checklist

Official dataset releases (`sift_dataset_v1.0.0`) must pass 7 automated quality gates:
1. **Source Authorization:** Source permission status verified as `AUTHORIZED`.
2. **Zero Unredacted PII:** Clean audit across phone numbers, emails, employee IDs, and IP addresses.
3. **100% Annotation Completeness:** All records in `CONSENSUS_ACCEPTED` or `ADJUDICATED` state.
4. **Taxonomy Conformance:** Enums strictly match taxonomy v1.0.
5. **Evidence Span Invariance:** Exact character slice matching.
6. **Zero Cross-Split Leakage:** Incident event grouping and duplicate cluster isolation across partitions.
7. **High-SIF Safety Floor:** Test split contains required representation of High-SIF observations.

---

## 6. Known Biases, Class Imbalance & Limitations

1. **Severe Class Imbalance:**  
   Like real-world industrial environments, `NON-SIF` and `LOW` observations typically comprise ~75–85% of total report volume, while `CRITICAL` represents 5–10%. Models evaluated on this dataset must prioritize **High-SIF Recall ($\ge 95\%$)** over raw accuracy.
2. **Facility & Activity Concentration:**  
   Heavy drilling and plant operations generate higher reporting densities than passive pipeline transport routes.
3. **Frontline Reporting Variation:**  
   Narrative length and descriptive fidelity vary significantly across contractor vs. permanent operator submissions.

---

## 7. Partitioning & Temporal Split Strategy

To ensure genuine out-of-time evaluation and prevent data leakage:
- **70% TRAIN SPLIT:** Chronologically older historical observations.
- **15% VALIDATION SPLIT:** Chronologically intermediate observations (used for hyperparameter tuning and threshold calibration).
- **15% TEST SPLIT:** Chronologically latest "out-of-time" observations (strictly read-only).
- **Incident & Duplicate Cluster Grouping:** All reports belonging to the same physical incident (`incident_id`) or sharing near-duplicate text ($\ge 0.85$ Jaccard similarity) are kept within the same partition.
