# SIFT Dataset Quality & Lineage Report: `sift_sim_dataset` (v0.1.0)

**Build Timestamp:** `2026-08-30T16:24:28.429674+00:00`  
**Taxonomy Version:** `1.0`  
**Random Seed:** `42`  
**Split Strategy:** `Temporal Stratified Grouping with Event & Duplicate Isolation (70/15/15)`

---

## 1. Executive Quality Summary

| Metric | Count / Status | Notes |
| :--- | :--- | :--- |
| **Source Records Ingested** | `2` | Initial raw record pool |
| **Validated Eligible Records** | `2` | Passed schema & taxonomy audits |
| **Invalid / Rejected Records** | `0` | Failed validation checks |
| **Exact Duplicates (SHA-256)** | `0` | Deterministic hash collision |
| **Near-Duplicates (Jaccard $\ge 0.85$)** | `0` | Grouped to prevent cross-split leakage |
| **PII Flagged Records** | `0` | Sanitized / Flagged under governance |
| **Cross-Split Leakage Check** | **PASSED (Zero Leakage)** | Event & duplicate cluster isolation |
| **High-SIF Count in Test Split** | `0` | Safety-critical evaluation floor |

---

## 2. Partition Summary

| Split | Record Count | CRITICAL/HIGH SIF | High-SIF Ratio |
| :--- | :--- | :--- | :--- |
| **TRAIN (70%)** | `1` | `1` | `100.0%` |
| **VALIDATION (15%)** | `0` | `0` | `0%` |
| **TEST (15%)** | `1` | `0` | `0.0%` |

---

## 3. Categorical Class Distributions

### SIF Potential Tier (Overall)

- **CRITICAL:** `1` (50.0%)
- **NON-SIF:** `1` (50.0%)

### Precursor Category Multi-Label Distribution

- **Energy Isolation:** `1`
- **Procedural Safety:** `1`

### Top Primary Hazards

- **Operational Hazard Exposure:** `2`

### Barrier Status Breakdown


---

## 4. Pipeline Warnings & Quality Alerts

> [!WARNING]
> HIGH-SIF ALERT: Test split contains only 0 CRITICAL/HIGH observations (minimum target: 3)
