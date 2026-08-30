# SIFT Human Annotation Protocol & Guidelines

**Guideline Version:** 1.0  
**Target Audience:** HSE Specialists, Safety Engineers, Annotation Team Leads, Adjudicators  

---

## 1. Objective

This document establishes the official standard operating procedures for creating gold-standard human-annotated datasets for SIFT. High-quality annotations are the foundation of reliable machine learning models. 

Every annotator must follow these instructions strictly to ensure high inter-annotator agreement (Cohen's Kappa $\kappa \ge 0.85$).

---

## 2. Unit of Annotation

Annotators will review a single safety observation at a time. The annotation interface presents:
1. **Report ID:** Unique system tracking number (e.g. `SIF-2026-00124`).
2. **Raw Report Text:** Exact, unmodified narrative entered by the field operator.
3. **Report Type:** Near Miss, Unsafe Act, Unsafe Condition, or Incident.
4. **Contextual Metadata:** Facility Name, Operating Basin, and Activity (if supplied).

> [!WARNING]
> **No AI Leakage:**  
> When annotating dataset ground truth, human annotators must **never** be shown previous AI predictions or rule-based classifications. Independent human judgment is strictly required.

---

## 3. Double-Blind Multi-Annotator Workflow

```
                             RAW SAFETY REPORT
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
             ANNOTATOR A (HSE)                 ANNOTATOR B (HSE)
                    │                                 │
                    ▼                                 ▼
             ANNOTATION A                      ANNOTATION B
                    │                                 │
                    └────────────────┬────────────────┘
                                     │
                         AGREEMENT CHECK (KAPPA)
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
                 MATCHING                       DISCREPANCY
                     │                               │
                     ▼                               ▼
             DIRECT CONSENSUS                 EXPERT ADJUDICATION
                     │                     (Lead Investigator Review)
                     │                               │
                     └───────────────┬───────────────┘
                                     │
                                     ▼
                           FINAL GOLD GROUND TRUTH
                              (DatasetRecord)
```

1. **Phase 1 (Independent Annotation):** Two qualified HSE safety specialists independently annotate the report.
2. **Phase 2 (Agreement Audit):** If both annotators agree on all core categorical labels (SIF Potential, Precursor Category, Life-Saving Rule, Barrier Status), the record is automatically accepted into the dataset.
3. **Phase 3 (Adjudication):** If annotators disagree on any primary label or SIF tier, the record is flagged for **Lead Safety Specialist Adjudication**. Categorical labels are **never averaged**; the adjudicator evaluates both rationale notes and assigns the final authoritative label with `disagreement_notes`.

---

## 4. Key Conceptual Boundaries & Pitfalls

### 4.1 SIF Potential vs. Actual Injury
- **Rule:** Do NOT annotate based on the physical injury outcome.
- **Example:** A worker slips while walking across a level gravel path and fractures a wrist $\rightarrow$ Actual injury is moderate, but SIF Potential is **LOW / MEDIUM** (low energy, non-life-altering).
- **Counter-Example:** A 4-inch pressurized gas fitting blows off at 50 bar and misses a worker's head by 30 cm $\rightarrow$ Actual injury is ZERO, but SIF Potential is **CRITICAL** (catastrophic high-energy release in direct line of fire).

### 4.2 SIF CRITICAL vs. SIF HIGH
- **CRITICAL:** High-energy hazard was uncontained in an active work zone with **zero surviving barriers** (immediate life-or-death scenario).
  - *Example:* Operator inside separator with 42 ppm H2S and no ventilation.
- **HIGH:** High-energy hazard was present with a **compromised secondary barrier**, or required one additional failure to become fatal.
  - *Example:* Worker on scaffold at 6 meters with harness on, but lanyard attached to an unrated electrical conduit rather than an anchor point.

### 4.3 SIF Precursor vs. Hazard
- **Hazard:** The source of potential harm or energy (e.g. *Pressurized Natural Gas*, *Toxic H2S Gas*, *Suspended Tubular Load*).
- **SIF Precursor:** The operational circumstance or missing barrier that permits that energy to reach personnel (e.g. *Breaking flange without Lockout/Tagout*, *Entering confined space without gas clearance*).

### 4.4 Failed Barrier vs. Absent Evidence
- If the report explicitly states a safety control did not perform or was missing $\rightarrow$ Classify as **FAILED**.
- If the report makes no mention of whether a barrier existed or was attempted $\rightarrow$ Classify as **UNKNOWN**. Do not fabricate a failure if the operator did not describe it.

---

## 5. Grounded Evidence Extraction Protocol (TASK-009)

Every SIF classification must be supported by at least one **verifiable evidence span**.

### Rules for Span Selection:
1. **Exact Substring Only:** The extracted text must be an exact, continuous character substring of the raw text.
2. **Minimal Sufficient Span:** Select the shortest phrase that captures the hazard and barrier breakdown.
   - *Good Span:* `"loosening bolts without proper isolation"`
   - *Bad Span (Too long):* `"During the morning shift at 09:00 hrs the operator started loosening bolts without proper isolation because the shift was ending."`
3. **Character Offsets (`start_offset`, `end_offset`):**  
   Record exact 0-indexed character offsets such that:
   `raw_text[start_offset:end_offset] == text`

---

## 6. Annotated Example Walkthrough

### Example Report:
> *"During routine morning inspection of Gas Compressor #2, noticed the discharge bypass valve vibrating excessively. Upon closer look, 2 of the 4 flange stud bolts were completely sheared off under 45 bar gas pressure. Immediately initiated emergency depressurization before flange gasket blowout."*

### Gold Standard Annotation Output:
```json
{
  "report_id": "SIF-2026-00412",
  "report_type": "Near Miss",
  "labels": {
    "sif_potential": "CRITICAL",
    "sif_precursor": "YES",
    "primary_precursor": "Energy Isolation",
    "secondary_precursors": ["Process Safety"],
    "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
    "life_saving_rule": "Energy Isolation",
    "barriers": [
      {
        "barrier_name": "Pressure Containment & Flange Stud Integrity",
        "status": "FAILED",
        "barrier_type": "Engineering / Physical Barrier",
        "description": "2 of 4 studs sheared off under 45 bar gas pressure"
      },
      {
        "barrier_name": "Emergency Depressurization & Manual Intervention",
        "status": "EFFECTIVE",
        "barrier_type": "Administrative / Procedural Barrier",
        "description": "Operator initiated emergency blowdown before total gasket blowout"
      }
    ],
    "evidence_spans": [
      {
        "text": "2 of the 4 flange stud bolts were completely sheared off under 45 bar gas pressure",
        "start_offset": 128,
        "end_offset": 210
      }
    ],
    "urgency_score": 96,
    "potential_consequence": "Catastrophic flange rupture resulting in high-pressure natural gas jet release, vapor cloud ignition, and fatal blast impact."
  },
  "annotation": {
    "annotator_id": "HSE-EXP-04",
    "adjudicator_id": "HSE-LEAD-01",
    "review_status": "ADJUDICATED",
    "taxonomy_version": "1.0",
    "disagreement_notes": "Annotator A flagged HIGH; Adjudicator elevated to CRITICAL due to 45 bar pressure with 50% mechanical bolt failure."
  }
}
```
