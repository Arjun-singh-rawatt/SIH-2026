# SIFT Canonical Dataset & Record Schema

**Schema Version:** 1.0  
**Format:** JSON Lines (`.jsonl`)  
**Encoding:** UTF-8  

---

## 1. Overview

Every training, validation, testing, and benchmark dataset in SIFT must adhere to the **Canonical SIFT JSONL Dataset Record Format**. Each line of a `.jsonl` file represents one complete, self-contained, validated safety observation with operational context, structured labels, and annotation metadata.

---

## 2. Field-Level Data Dictionary

### 2.1 Top-Level Record Fields

| Field Name | Type | Required | Description | Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `schema_version` | `string` | **Yes** | Dataset record schema version | Fixed to `"1.0"` |
| `report_id` | `string` | **Yes** | Unique safety report identifier | Must match pattern `^SIF-\d{4}-\d{5}$` |
| `split` | `string` | No | Data split assignment | `"TRAIN"`, `"VALIDATION"`, `"TEST"` |
| `raw_text` | `string` | **Yes** | Unmodified narrative entered by field reporter | Min length: 5 chars; Unicode clean |
| `report_type` | `string` | **Yes** | Safety observation classification | `"Near Miss"`, `"Unsafe Act"`, `"Unsafe Condition"`, `"Incident"` |
| `context` | `object` | **Yes** | Operational metadata container | See §2.2 |
| `labels` | `object` | **Yes** | Ground truth task labels container | See §2.3 |
| `annotation` | `object` | **Yes** | Human annotation audit container | See §2.4 |

---

### 2.2 `context` Object

| Field Name | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `facility_id` | `string` | **Yes** | OIL Operational Facility Code | `"FAC-DIG-02"` |
| `facility_name` | `string` | No | Full facility name | `"Digboi Field & Production Complex"` |
| `region` | `string` | No | Operating geological basin | `"Upper Assam Basin"` |
| `location` | `string` | No | Specific skid or plant section | `"Compressor Area, Train-2 Header"` |
| `activity` | `string` | **Yes** | Active operational work task | `"Maintenance"` |

---

### 2.3 `labels` Object

| Field Name | Type | Required | Description | Permitted Values / Constraints |
| :--- | :--- | :--- | :--- | :--- |
| `sif_potential` | `string` | **Yes** | SIF Potential severity tier | `"CRITICAL"`, `"HIGH"`, `"MEDIUM"`, `"LOW"`, `"NON-SIF"` |
| `sif_precursor` | `string` | **Yes** | SIF Precursor flag | `"YES"`, `"NO"`, `"POTENTIAL"` |
| `primary_precursor` | `string` | **Yes** | Dominant precursor category | Must match `PrecursorCategory` in `TAXONOMY.md` |
| `secondary_precursors` | `array[string]` | **Yes** | Additional multi-label precursor mechanisms | Array of valid `PrecursorCategory` strings |
| `primary_hazard` | `string` | **Yes** | Primary physical hazard | Standardized hazard string |
| `secondary_hazards` | `array[string]` | No | Additional hazards present | Array of standardized strings |
| `life_saving_rule` | `string` | **Yes** | Mapped IOGP Life-Saving Rule | Standardized rule name |
| `barriers` | `array[object]` | **Yes** | Evaluated safety barriers | Array of `BarrierAssessment` objects (§2.3.1) |
| `evidence_spans` | `array[object]` | **Yes** | Grounded evidence text snippets | Array of `EvidenceSpan` objects (§2.3.2) |
| `urgency_score` | `integer` | **Yes** | Triage urgency index | Range: `0` to `100` inclusive |
| `potential_consequence` | `string` | No | Worst-case realistic consequence | Free text description |
| `ai_explanation` | `string` | No | Grounded explanatory sentence | Hallucination-free rationale |

#### 2.3.1 `barriers` Item Schema
```json
{
  "barrier_name": "string (Required)",
  "status": "FAILED | WEAK | EFFECTIVE | UNKNOWN (Required)",
  "barrier_type": "Engineering / Physical Barrier | Administrative / Procedural Barrier | Behavioral / Last Line of Defense (PPE)",
  "description": "string (Optional)"
}
```

#### 2.3.2 `evidence_spans` Item Schema & Offset Invariant
```json
{
  "text": "string (Exact substring)",
  "start_offset": "integer (0-indexed, >= 0)",
  "end_offset": "integer (0-indexed, > start_offset)"
}
```

> [!IMPORTANT]
> **Strict Offset Invariant:**  
> `raw_text[start_offset:end_offset] == text`  
> Automated validators will reject any dataset record where the slice of `raw_text` does not match `text` character-for-character.

---

### 2.4 `annotation` Object

| Field Name | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `annotator_id` | `string` | **Yes** | Primary human annotator ID | `"HSE-EXP-04"` |
| `adjudicator_id` | `string` | No | Resolving senior specialist ID | `"HSE-LEAD-01"` |
| `review_status` | `string` | **Yes** | Review lifecycle state | `"ADJUDICATED"` |
| `taxonomy_version` | `string` | **Yes** | Taxonomy version used | `"1.0"` |
| `annotated_at` | `string` | **Yes** | ISO-8601 UTC timestamp | `"2026-08-30T10:15:30Z"` |
| `disagreement_notes` | `string` | No | Adjudication resolution notes | `"Reclassified from HIGH to CRITICAL"` |

---

## 3. Complete JSONL Record Example

```json
{
  "schema_version": "1.0",
  "report_id": "SIF-2026-00042",
  "split": "TRAIN",
  "raw_text": "While tripping 5-inch drill pipes on Rig-42, the auxiliary air hoist wire rope snapped near the thimble clamp under a 3.2-ton shock load. The suspended drill collar swung erratically through the rotary table area, narrowly missing two roughnecks standing directly in the line of fire.",
  "report_type": "Near Miss",
  "context": {
    "facility_id": "FAC-NHK-06",
    "facility_name": "Naharkatiya Deep Drilling Hub",
    "region": "Assam Shelf",
    "location": "Rig Floor NHK-42, Derrick Substructure",
    "activity": "Drilling Operations"
  },
  "labels": {
    "sif_potential": "CRITICAL",
    "sif_precursor": "YES",
    "primary_precursor": "Lifting Operations",
    "secondary_precursors": ["Line of Fire"],
    "primary_hazard": "Dropped Heavy Object / Line of Fire",
    "secondary_hazards": ["Stored / Pressurized Hydrocarbon Energy"],
    "life_saving_rule": "Safe Mechanical Lifting",
    "barriers": [
      {
        "barrier_name": "Rigging Equipment Integrity & Hoist Wire Clamp",
        "status": "FAILED",
        "barrier_type": "Engineering / Physical Barrier",
        "description": "Wire rope snapped at thimble under 3.2-ton shock load"
      },
      {
        "barrier_name": "Red Zone / Rotary Table Exclusion Zone",
        "status": "FAILED",
        "barrier_type": "Administrative / Procedural Barrier",
        "description": "Two roughnecks were standing within the line of fire trajectory"
      }
    ],
    "evidence_spans": [
      {
        "text": "auxiliary air hoist wire rope snapped near the thimble clamp under a 3.2-ton shock load",
        "start_offset": 48,
        "end_offset": 136
      },
      {
        "text": "narrowly missing two roughnecks standing directly in the line of fire",
        "start_offset": 204,
        "end_offset": 273
      }
    ],
    "urgency_score": 98,
    "potential_consequence": "Direct fatal crushing impact from uncontrolled 3.2-ton suspended drill collar on rig floor personnel.",
    "ai_explanation": "Critical mechanical rigging failure occurred under load while personnel were positioned in the line of fire without enforced barricading."
  },
  "annotation": {
    "annotator_id": "HSE-EXP-02",
    "adjudicator_id": "HSE-LEAD-01",
    "review_status": "ADJUDICATED",
    "taxonomy_version": "1.0",
    "annotated_at": "2026-08-30T14:22:00Z",
    "disagreement_notes": "Unanimous consensus between annotators on CRITICAL SIF and Line of Fire barrier failure."
  }
}
```
