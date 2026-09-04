# SIFT Dataset Engineering & Validation Pipeline

**Specification Version:** 1.0  
**Effective Date:** 2026-08-30  
**Target Scope:** Data Engineering, Human Annotation Workflows, Dataset Quality Assurance, Dataset Lineage  

---

## 1. Executive Architecture Overview

The SIFT Data Pipeline transforms raw safety observations, field reports, and incident logs into validated, cryptographically hashed, leakage-controlled Machine Learning datasets.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SIFT DATA PIPELINE FLOW                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   RAW SOURCES (JSON / JSONL / CSV / PostgreSQL SafetyReports)               │
│                                │                                            │
│                                ▼                                            │
│   INGESTION & FIELD MAPPING (`DataIngester` / `DatabaseExporter`)           │
│   - Normalizes external column keys to canonical SIFT fields                │
│   - Preserves source provenance metadata (source_file, timestamp)           │
│                                │                                            │
│                                ▼                                            │
│   DETERMINISTIC NORMALIZATION (`normalize_text`, `compute_content_hash`)    │
│   - Unicode NFC composition & newline normalization (\r\n -> \n)            │
│   - Preserves exact technical safety vocabulary & character invariants      │
│                                │                                            │
│                                ▼                                            │
│   GOVERNANCE & PII AUDIT (`PIIDetector`, `GovernanceChecker`)               │
│   - Detects & flags emails, phone numbers, employee IDs, personal names     │
│   - Inspects for input feature label leakage and post-event contamination   │
│                                │                                            │
│                                ▼                                            │
│   DOUBLE-BLIND HUMAN ANNOTATION (`AnnotationManager`)                       │
│   - Strips all AI predictions (ai_*) to prevent cognitive bias              │
│   - Audits dual-annotator consensus & computes Cohen's Kappa (κ)            │
│   - Flags discrepancies for Lead Safety Specialist Adjudication             │
│                                │                                            │
│                                ▼                                            │
│   CANONICAL VALIDATION ENGINE (`DatasetValidator`)                          │
│   - Enforces Pydantic DatasetRecord schema                                  │
│   - Asserts raw_text[start:end] == evidence_span.text invariant             │
│   - Validates all categories against TAXONOMY.md (Taxonomy Version 1.0)     │
│                                │                                            │
│                                ▼                                            │
│   DEDUPLICATION & CLUSTERING (`DuplicateDetector`)                          │
│   - SHA-256 exact content hash collision detection                          │
│   - Pairwise n-gram token Jaccard similarity (≥ 0.85 near-duplicate grouping│
│                                │                                            │
│                                ▼                                            │
│   LEAKAGE-SAFE TEMPORAL SPLITTING (`DatasetSplitter`)                       │
│   - Event & cluster-grouped partitioning (Train 70% / Val 15% / Test 15%)   │
│   - Deterministic tie-breaking with seed (random_seed = 42)                 │
│   - Verifies zero cross-split duplicate or event overlap                    │
│   - Audits High-SIF representation floor in test split                      │
│                                │                                            │
│                                ▼                                            │
│   VERSIONED DATASET RELEASE & MANIFEST (`DatasetManifestGenerator`)         │
│   - Generates SHA-256 manifest: sift_dataset_v{VERSION}_manifest.json       │
│   - Generates lineage metadata: sift_dataset_v{VERSION}_metadata.json       │
│   - Produces machine JSON and human Markdown Quality Reports                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory Layout Standards

All data artifacts are partitioned across strictly segregated lifecycle directories:

```text
SIFT/
├── data/
│   ├── raw/                  # Immutable original input files (CSV, JSON, JSONL)
│   ├── interim/              # Normalized, field-mapped intermediate records
│   ├── processed/            # Sanitized, PII-checked candidate records
│   ├── annotations/          # Double-blind task exports, annotator submissions
│   ├── validated/            # Validated golden DatasetRecords ready for splitting
│   ├── splits/               # Versioned train, validation, and test split JSONL files
│   ├── metadata/             # Quality reports, manifests, dataset registry
│   └── fixtures/             # Explicit synthetic test fixtures
│
├── data_pipeline/            # Core Python data engineering library
│   ├── __init__.py
│   ├── ingestion.py          # Multi-format ingestion and DB export
│   ├── normalization.py      # Unicode normalization & offset verification
│   ├── governance.py         # PII detection & label leakage auditing
│   ├── validation.py         # Schema, taxonomy, and span offset validator
│   ├── duplicates.py         # SHA-256 deduplication & Jaccard near-duplicate clusters
│   ├── annotations.py        # Double-blind export, Kappa agreement, adjudication
│   ├── splitting.py          # Temporal & incident-event grouped splitting
│   ├── metrics.py            # Class distributions & quality analytics
│   └── manifest.py           # Cryptographic manifest & report generation
│
└── scripts/                  # CLI command suite
    ├── build_dataset.py      # Master reproducible build orchestrator
    ├── ingest_dataset.py     # Standalone ingestion
    ├── validate_dataset.py   # Standalone validation runner
    ├── detect_duplicates.py  # Standalone duplicate & cluster scanner
    ├── detect_leakage.py     # Standalone split & label leakage auditor
    ├── split_dataset.py      # Standalone temporal dataset splitter
    ├── export_db_dataset.py  # Database export with training eligibility checks
    └── manage_annotations.py # Double-blind export, Kappa audit & adjudication
```

---

## 3. Command-Line Reference & Workflows

### 3.1 Master End-to-End Build
Executes all pipeline phases in a single reproducible command:
```bash
# Release Build
python scripts/build_dataset.py \
    --source data/raw/source_records.jsonl \
    --version 1.0.0 \
    --output-dir data \
    --train-ratio 0.70 \
    --val-ratio 0.15 \
    --test-ratio 0.15 \
    --seed 42

# Dry Run Mode (audits quality and distributions without writing release files)
python scripts/build_dataset.py \
    --source data/raw/source_records.jsonl \
    --version 1.0.0 \
    --dry-run
```

### 3.2 Raw Data Ingestion
Ingests CSV, JSON, or JSONL files into normalized interim records:
```bash
python scripts/ingest_dataset.py \
    --input data/raw/field_observations.csv \
    --output data/interim/normalized.jsonl
```

### 3.3 Dataset Validation
Audits any `.jsonl` dataset file against canonical Pydantic schemas and taxonomy rules:
```bash
python scripts/validate_dataset.py \
    --input data/validated/dataset.jsonl \
    --strict \
    --output-report data/metadata/validation_report.json
```

### 3.4 Duplicate & Cluster Detection
Detects exact SHA-256 text collisions and pairwise near-duplicates ($\ge 0.85$ Jaccard similarity):
```bash
python scripts/detect_duplicates.py \
    --input data/interim/normalized.jsonl \
    --threshold 0.85 \
    --output-report data/metadata/duplicate_report.json
```

### 3.5 Leakage & Governance Auditing
Audits dataset partitions for cross-split duplicates, event ID overlap, and label leakage:
```bash
python scripts/detect_leakage.py \
    --train data/splits/sift_dataset_v1.0.0_train.jsonl \
    --val data/splits/sift_dataset_v1.0.0_val.jsonl \
    --test data/splits/sift_dataset_v1.0.0_test.jsonl \
    --output-report data/metadata/leakage_audit.json
```

### 3.6 Double-Blind Annotation Management
Exports bias-free annotation tasks and audits inter-annotator agreement:
```bash
# 1. Export double-blind tasks (AI predictions stripped)
python scripts/manage_annotations.py export \
    --input data/raw/unannotated_reports.jsonl \
    --output data/annotations/batch_001_blind.jsonl

# 2. Audit paired annotator submissions & compute Kappa agreement
python scripts/manage_annotations.py audit \
    --annotator-a data/annotations/sub_annotator_a.jsonl \
    --annotator-b data/annotations/sub_annotator_b.jsonl \
    --output-consensus data/validated/consensus_batch_001.jsonl
```

### 3.7 Database Export
Exports human-adjudicated records from the database with strict eligibility verification:
```bash
# Gold Ground Truth Export (requires human review sign-off)
python scripts/export_db_dataset.py --output data/raw/db_ground_truth.jsonl

# Demo Dataset Export (clearly marked as synthetic demo data)
python scripts/export_db_dataset.py --output data/raw/demo_seed_export.jsonl --demo
```

---

## 4. Key Engineering Invariants & Quality Standards

1. **Character Offset Invariant:**  
   `raw_text[start_offset:end_offset] == evidence_span.text`  
   Every evidence span extracted must match the raw text slice character-for-character.
2. **Double-Blind Independence:**  
   Human annotators creating ground-truth labels are never exposed to machine predictions (`ai_*`), confidence ratings, or prior reviewer notes.
3. **Event & Cluster Isolation:**  
   Observations originating from the same physical incident (`incident_id`) or sharing near-duplicate content ($\ge 0.85$ similarity) are strictly confined to the same dataset split.
4. **Cryptographic Lineage:**  
   Every release dataset is accompanied by a SHA-256 manifest and complete metadata specification recorded in the central dataset registry.
