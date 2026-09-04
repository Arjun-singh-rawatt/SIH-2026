# SIFT AI Inference & Serving Contract

**Contract Version:** 1.0  
**Status:** Active FastAPI Serving Specification  
**Applies To:** `api/app/ai/`, `api/app/api/v1/endpoints/analysis.py`, `AIProvider` Interface  

---

## 1. Fast, Reliable REST Interface

The AI analysis pipeline exposes a synchronous, low-latency endpoint consumed by the SIFT frontend and batch ingestion workers:

`POST /api/v1/reports/analyze`

### 1.1 Request Payload Schema (`AnalyzeRequest`)
```json
{
  "report_text": "string (min_length: 5, required)",
  "report_type": "string (default: 'Near Miss')",
  "facility_id": "string (default: 'FAC-DIG-02')",
  "facility_name": "string (optional)",
  "region": "string (optional)",
  "location": "string (default: 'Main Processing Section')",
  "activity": "string (default: 'Maintenance')"
}
```

### 1.2 Response Payload Schema (`ReportAnalysisResult`)
```json
{
  "sif_potential": "CRITICAL | HIGH | MEDIUM | LOW | NON-SIF",
  "sif_precursor": "YES | NO | POTENTIAL",
  "confidence": 96.5,
  "urgency_score": 94,
  "precursor_category": "Energy Isolation",
  "activity": "Maintenance",
  "primary_hazard": "Stored / Pressurized Hydrocarbon Energy",
  "life_saving_rule": "Energy Isolation",
  "failed_barrier": "Zero Energy Verification & Isolation Certificate",
  "barrier_status": "FAILED | WEAK | EFFECTIVE | UNKNOWN",
  "potential_consequence": "Catastrophic release of pressurized hydrocarbon gas resulting in fatal blast impact.",
  "evidence_phrase": "without proper isolation; still pressurized with 35 bar natural gas",
  "evidence_phrases": [
    "without proper isolation",
    "still pressurized with 35 bar natural gas"
  ],
  "ai_explanation": "The activity involved servicing equipment on a pressurized hydrocarbon system without positive isolation."
}
```

---

## 2. Confidence Calibration Specification

> [!CAUTION]
> **Confidence $\ne$ Urgency $\ne$ Probability of Injury**  
> `confidence` measures the model's certainty in its categorical predictions. It must **never** be conflated with the severity of the hazard or the probability of an injury occurring.

- **API Range:** `0.0` to `100.0%` (floating point).
- **Calibration Requirement:** Raw softmax probabilities from neural models must undergo **Temperature Scaling** on the validation set before serving to ensure $\mathbb{E}[\text{accuracy} \mid \text{confidence} = p] = p$.

---

## 3. Baseline Heuristic Urgency Scoring Formula (v1.0)

Urgency Score ($U \in [0, 100]$) is computed deterministically using the versioned **Baseline Heuristic Risk Formula (v1.0)**:

$$U = W_{\text{potential}} + W_{\text{hazard}} + W_{\text{barrier}} + W_{\text{activity}}$$

### Component Weights:
1. **SIF Potential Tier ($W_{\text{potential}}$, Max 40 pts):**
   - `CRITICAL`: $40\text{ pts}$
   - `HIGH`: $30\text{ pts}$
   - `MEDIUM`: $18\text{ pts}$
   - `LOW`: $8\text{ pts}$
   - `NON-SIF`: $0\text{ pts}$
2. **Hazard Severity ($W_{\text{hazard}}$, Max 25 pts):**
   - High-Pressure Hydrocarbons / Toxic H2S Gas: $25\text{ pts}$
   - Dropped Heavy Objects / Fall from Height: $20\text{ pts}$
   - Electrical / Rotating Machinery: $15\text{ pts}$
   - Low-energy / General Industrial: $5\text{ pts}$
3. **Barrier Failure Status ($W_{\text{barrier}}$, Max 20 pts):**
   - `FAILED` (Physical/Engineering Barrier): $20\text{ pts}$
   - `FAILED` (Administrative Barrier): $15\text{ pts}$
   - `WEAK`: $10\text{ pts}$
   - `UNKNOWN`: $5\text{ pts}$
   - `EFFECTIVE`: $0\text{ pts}$
4. **Activity Exposure Context ($W_{\text{activity}}$, Max 15 pts):**
   - Drilling / Live Plant Operations / Confined Vessel Entry: $15\text{ pts}$
   - Standard Plant Maintenance / Rigging: $10\text{ pts}$
   - Inspection / Transportation: $5\text{ pts}$

### Triage Priority Bands:
- `80 – 100`: **CRITICAL PRIORITY** (Immediate executive attention required)
- `60 – 79`: **HIGH PRIORITY** (Action item assignment within 24 hours)
- `30 – 59`: **MODERATE PRIORITY** (Standard supervisory review)
- `0 – 29`: **LOW PRIORITY** (Routine documentation)

---

## 4. Dual Classification & Auditability Invariant

The database model `SafetyReport` enforces complete separation between machine inference and certified human validation:

```
                  ┌─────────────────────────────────────┐
                  │          RAW OBSERVATION            │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │       ORIGINAL AI PREDICTION        │
                  │ (ai_sif_potential, ai_confidence,   │
                  │  ai_failed_barrier, ai_evidence)    │
                  │       [IMMUTABLE AUDIT LOG]         │
                  └──────────────────┬──────────────────┘
                                     │
                                     ▼
                  ┌─────────────────────────────────────┐
                  │      HUMAN REVIEW & VALIDATION      │
                  │ (final_sif_potential, reviewer_id,  │
                  │  reviewer_notes, reviewed_at)       │
                  │     [AUTHORITATIVE GROUND TRUTH]    │
                  └─────────────────────────────────────┘
```

- **Rule 1:** `ai_*` fields are recorded at ingestion and **never updated or overwritten**.
- **Rule 2:** `final_*` fields capture the certified HSE Safety Officer's human sign-off.
- **Rule 3:** The UI displays both side-by-side to ensure full operational transparency and auditability.
