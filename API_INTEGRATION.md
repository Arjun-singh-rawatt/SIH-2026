# SIFT — Frontend to Backend API Integration Specification

This document provides complete documentation of the full-stack integration between the React frontend and the FastAPI Python backend for **SIFT (Safety Intelligence & Fatality-risk Tracking)**.

---

## 1. Architecture Overview

The SIFT application follows a clean layered client-server architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      React 19 Frontend                      │
│                                                             │
│  [Pages & Views]                                            │
│  Dashboard · Reports · ReportDetails · AnalyzeReport ·      │
│  ReviewQueue · Actions · Facilities · Intelligence · Rules  │
│                               ▲                             │
│                               │                             │
│  [State & Contexts]           ▼                             │
│  ReportsContext · ThemeContext · AuthContext                │
│                               ▲                             │
│                               │                             │
│  [Domain Service Layer]       ▼                             │
│  reportService · actionService · analyticsService ·        │
│  facilityService · intelligenceService · lifeSavingRules    │
│                               ▲                             │
│                               │                             │
│  [Data Mapping Layer]         ▼                             │
│  mappers.js (snake_case API ◄──► camelCase UI Domain)       │
│                               ▲                             │
│                               │                             │
│  [HTTP Client Engine]         ▼                             │
│  apiClient.js (Fetch / URLSearchParams / Normalized Errors) │
└───────────────────────────────┬─────────────────────────────┘
                                │ HTTP REST (JSON)
                                │ VITE_API_BASE_URL (http://localhost:8000/api/v1)
┌───────────────────────────────▼─────────────────────────────┐
│                   Python FastAPI Backend                    │
│                                                             │
│  [API Routers]                                              │
│  /health · /api/v1/dashboard · /api/v1/reports ·            │
│  /api/v1/reviews · /api/v1/actions · /api/v1/facilities ·   │
│  /api/v1/intelligence · /api/v1/life-saving-rules · /users  │
│                               ▲                             │
│                               │                             │
│  [Business Services & AI Engine]                            │
│  ReportService · AnalyticsService · AIClassificationEngine  │
│  VectorStoreService · ActionItemService                     │
│                               ▲                             │
│                               │                             │
│  [Data Access & ORM]          ▼                             │
│  SQLAlchemy Async Session · PostgreSQL / SQLite Models      │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Environment Configuration

The frontend dynamically discovers the backend API base URL using Vite environment variables:

| Variable Name | Default Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Root URL for all v1 REST API endpoints |

Configuration files:
- `.env`: Active local developer environment.
- `.env.example`: Template for staging and production deployments.

---

## 3. Centralized API Client (`apiClient.js`)

Located at [`src/services/api/apiClient.js`](file:///Users/satyamkumar/Desktop/SIFT/src/services/api/apiClient.js).

### Key Features:
- **Methods**: `apiClient.get(endpoint, params)`, `apiClient.post(endpoint, body)`, `apiClient.patch(endpoint, body)`, `apiClient.delete(endpoint)`.
- **Query Parameter Sanitization**: Automatically filters out `null`, `undefined`, empty strings (`""`), and `"ALL"`.
- **Standardized Error Contracts**: Normalizes network and HTTP errors into an `ApiError` instance containing:
  ```javascript
  {
    status: 400 | 404 | 422 | 500 | 0,
    code: "VALIDATION_ERROR" | "NOT_FOUND" | "NETWORK_ERROR",
    message: "Human-readable message",
    details: [...]
  }
  ```

---

## 4. Data Mappers (`mappers.js`)

Located at [`src/services/api/mappers.js`](file:///Users/satyamkumar/Desktop/SIFT/src/services/api/mappers.js).

Bridges FastAPI `snake_case` models with React `camelCase` domain objects:

| Backend Field (`snake_case`) | Frontend Domain Field (`camelCase`) | Notes |
| :--- | :--- | :--- |
| `report_id` | `reportId` | e.g., `"SIF-2026-00124"` |
| `facility_id` | `facilityId` | e.g., `"FAC-DIG-02"` |
| `facility_name` | `facilityName` | e.g., `"Digboi Field Complex"` |
| `raw_report_text` | `rawReportText` | Full field observation narrative |
| `report_type` | `reportType` | `"Near Miss"`, `"Unsafe Act"`, etc. |
| `primary_hazard` | `primaryHazard` | e.g., `"Pressurized Natural Gas Line"` |
| `sif_potential` | `sifPotential` | `"CRITICAL"`, `"HIGH"`, `"MEDIUM"`, `"LOW"` |
| `urgency_score` | `urgencyScore` | Numeric integer (0 - 100) |
| `life_saving_rule` | `lifeSavingRule` | IOGP standardized rule name |
| `failed_barrier` | `failedBarrier` | Specific barrier failure mode |
| `barrier_status` | `barrierStatus` | `"FAILED"`, `"DEGRADED"`, `"EFFECTIVE"` |
| `evidence_phrase` | `evidencePhrase` | Extracted key phrase |
| `evidence_phrases` | `evidencePhrases` | Array of highlighted text segments |
| `ai_sif_potential` | `aiSifPotential` | Original AI prediction |
| `final_sif_potential` | `finalSifPotential` | HSE human reviewer final sign-off |
| `review_status` | `reviewStatus` | `"PENDING"`, `"APPROVED"`, `"MODIFIED"` |
| `action_id` | `actionId` | e.g., `"ACT-2026-0045"` |
| `due_date` | `dueDate` | ISO timestamp |

---

## 5. Domain Service Contracts

### 5.1 Reports Service (`reportService.js`)
- `reportService.getReports(filters, page, pageSize)`: `GET /api/v1/reports`
- `reportService.getReportById(id)`: `GET /api/v1/reports/{id}`
- `reportService.getReportStats()`: `GET /api/v1/reports/stats`
- `reportService.createReport(data)`: `POST /api/v1/reports`
- `reportService.updateReport(id, data)`: `PATCH /api/v1/reports/{id}`
- `reportService.deleteReport(id)`: `DELETE /api/v1/reports/{id}`
- `reportService.getReviewQueue(tab, page, pageSize)`: `GET /api/v1/reviews/queue`
- `reportService.getReviewSummary()`: `GET /api/v1/reviews/summary`
- `reportService.updateReportReview(id, data)`: `POST /api/v1/reports/{id}/review`

### 5.2 AI Safety Analysis Service (`analysisService.js`)
- `analysisService.analyzeReportText(rawText, metadata, onProgress)`: `POST /api/v1/reports/analyze`
  - Runs AI feature extraction, SIF classification, barrier diagnosis, and evidence extraction with UI visual progress updates.

### 5.3 Safety Intelligence & Analytics (`analyticsService.js`)
- `analyticsService.getDashboardMetrics()`: `GET /api/v1/dashboard/overview` -> `.summary`
- `analyticsService.getTrendData(timeRange)`: `GET /api/v1/dashboard/overview` -> `.trend`
- `analyticsService.getPrecursorBreakdown()`: `GET /api/v1/dashboard/overview` -> `.precursor_distribution`
- `analyticsService.getFacilityRiskRanking()`: `GET /api/v1/dashboard/overview` -> `.facility_ranking`
- `analyticsService.getActivityRiskBreakdown()`: `GET /api/v1/dashboard/overview` -> `.activity_ranking`
- `analyticsService.getBarrierFailureStats()`: `GET /api/v1/dashboard/overview` -> `.barrier_failures`
- `analyticsService.getPriorityAlerts()`: `GET /api/v1/dashboard/overview` -> `.priority_attention`

### 5.4 Actions & CAPA Service (`actionService.js`)
- `actionService.getActions(filters, page, pageSize)`: `GET /api/v1/actions`
- `actionService.getActionById(id)`: `GET /api/v1/actions/{id}`
- `actionService.getActionStats()`: `GET /api/v1/actions/stats`
- `actionService.createAction(data)`: `POST /api/v1/actions`
- `actionService.updateActionStatus(id, newStatus)`: `PATCH /api/v1/actions/{id}`
- `actionService.deleteAction(id)`: `DELETE /api/v1/actions/{id}`

### 5.5 Operational Facilities Service (`facilityService.js`)
- `facilityService.getFacilities(filters)`: `GET /api/v1/facilities`
- `facilityService.getFacilityById(id)`: `GET /api/v1/facilities/{id}` & `GET /api/v1/facilities/{id}/stats`

### 5.6 Intelligence & Pattern Detection (`intelligenceService.js`)
- `intelligenceService.getPatterns(filters)`: `GET /api/v1/intelligence/patterns`
- `intelligenceService.getPatternById(id)`: `GET /api/v1/intelligence/patterns/{id}`
- `intelligenceService.getPatternOverview()`: `GET /api/v1/intelligence/overview`
- `intelligenceService.getSimilarReports(reportId, topK)`: `GET /api/v1/intelligence/similar-reports/{id}`
- `intelligenceService.querySimilarReports(queryText, topK)`: `POST /api/v1/intelligence/similar-reports`

### 5.7 IOGP Life-Saving Rules (`lifeSavingRuleService.js`)
- `lifeSavingRuleService.getLifeSavingRules()`: `GET /api/v1/life-saving-rules`
- `lifeSavingRuleService.getRuleById(id)`: `GET /api/v1/life-saving-rules/{id}`

---

## 6. Dual Classification & Auditability

SIFT enforces complete auditability between Machine Learning inferences and Certified HSE Safety Officer decisions:

1. **AI Predictions**: Captured in immutable fields (`ai_sif_potential`, `ai_confidence`, `ai_evidence_phrase`, `ai_urgency_score`, `ai_failed_barrier`).
2. **Human Reviews**: Captured upon sign-off in audit fields (`final_sif_potential`, `reviewer_id`, `reviewer_notes`, `reviewed_at`, `review_status`).
3. **UI Presentation**: The report details view displays both original machine learning classifications and verified human sign-offs side-by-side.
