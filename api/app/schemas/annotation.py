"""Pydantic schemas and request/response contracts for SIFT Annotation Workbench."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator

from app.schemas.ai.taxonomy import (
    SIFPotentialLevel,
    SIFPrecursorFlag,
    PrecursorCategory,
    PrimaryHazardType,
    ActivityCategory,
    LifeSavingRuleIdentifier,
    SafetyBarrierCategory,
    BarrierStatusLevel,
)
from app.schemas.ai.dataset import DatasetEvidenceSpan, DatasetBarrierAssessment


class EvidenceSpanInput(BaseModel):
    """Input evidence span with character offsets."""
    text: str = Field(..., description="Exact substring from the observation narrative")
    start_offset: int = Field(..., ge=0, description="0-indexed start character offset")
    end_offset: int = Field(..., gt=0, description="0-indexed end character offset")

    @model_validator(mode="after")
    def validate_offsets(self) -> "EvidenceSpanInput":
        if self.end_offset <= self.start_offset:
            raise ValueError("end_offset must be strictly greater than start_offset")
        return self


class BarrierAssessmentInput(BaseModel):
    """Barrier assessment input."""
    barrier_name: str = Field(..., description="Standardized barrier name")
    status: str = Field(..., description="FAILED, WEAK, EFFECTIVE, UNKNOWN")
    barrier_type: str = Field(default="Engineering / Physical Barrier")
    description: Optional[str] = Field(default=None)


# ------------------------------------------------------------------------------
# Annotation Batch Schemas
# ------------------------------------------------------------------------------

class AnnotationBatchCreate(BaseModel):
    """Schema for creating a new dual-annotator batch."""
    batch_id: str = Field(..., description="Batch ID, e.g. BATCH-2026-001")
    name: str = Field(..., description="Descriptive batch name")
    source_id: str = Field(default="SRC-SIM-01")
    report_ids: List[str] = Field(..., min_length=1, description="List of safety report IDs")
    annotator_a_id: str = Field(..., description="User ID of primary annotator")
    annotator_b_id: str = Field(..., description="User ID of secondary annotator")
    is_demo: bool = Field(default=True)
    notes: Optional[str] = Field(default=None)


class AnnotationBatchSummary(BaseModel):
    """Progress counters for a batch."""
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    pending_tasks: int
    disagreement_tasks: int
    adjudicated_tasks: int


class AnnotationBatchRead(BaseModel):
    """Batch overview model."""
    id: str
    batch_id: str
    name: str
    source_id: str
    status: str
    annotation_protocol_version: str
    taxonomy_version: str
    record_count: int
    is_demo: bool
    notes: Optional[str] = None
    created_by_id: str
    created_at: datetime
    updated_at: datetime
    summary: Optional[AnnotationBatchSummary] = None


# ------------------------------------------------------------------------------
# Task & Submission Schemas
# ------------------------------------------------------------------------------

class AnnotationSubmissionRead(BaseModel):
    """Read schema for human annotation submission."""
    id: str
    assignment_id: str
    task_id: str
    annotator_id: str
    is_draft: bool
    sif_potential: Optional[str] = None
    sif_precursor: Optional[str] = None
    primary_hazard: Optional[str] = None
    secondary_hazards: Optional[List[str]] = None
    activity: Optional[str] = None
    primary_precursor: Optional[str] = None
    precursor_categories: Optional[List[str]] = None
    life_saving_rule: Optional[str] = None
    life_saving_rules: Optional[List[str]] = None
    barriers: Optional[List[Dict[str, Any]]] = None
    evidence_spans: Optional[List[Dict[str, Any]]] = None
    urgency_score: Optional[int] = None
    potential_consequence: Optional[str] = None
    notes: Optional[str] = None
    submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class AnnotationTaskRead(BaseModel):
    """List item for annotation tasks."""
    id: str
    batch_id: str
    report_id: str
    status: str
    order_index: int
    my_assignment_status: Optional[str] = None
    my_role_slot: Optional[str] = None
    is_draft_saved: bool = False
    is_submitted: bool = False


class AnnotationTaskDetail(BaseModel):
    """Detailed task view for independent blind annotator.
    
    CRITICAL: All AI fields and peer annotator work are stripped.
    """
    id: str
    batch_id: str
    batch_name: str
    batch_status: str
    is_demo_batch: bool
    report_id: str
    status: str
    order_index: int

    # Narrative & context
    raw_text: str
    report_type: str
    facility_id: str
    facility_name: Optional[str] = None
    region: Optional[str] = None
    location: Optional[str] = None
    activity: Optional[str] = None

    # Caller's assignment context
    my_role_slot: Optional[str] = None
    my_assignment_status: Optional[str] = None
    my_submission: Optional[AnnotationSubmissionRead] = None


class AnnotationDraftRequest(BaseModel):
    """Draft payload (all fields optional to allow work in progress)."""
    sif_potential: Optional[str] = None
    sif_precursor: Optional[str] = None
    primary_hazard: Optional[str] = None
    secondary_hazards: Optional[List[str]] = None
    activity: Optional[str] = None
    primary_precursor: Optional[str] = None
    precursor_categories: Optional[List[str]] = None
    life_saving_rule: Optional[str] = None
    life_saving_rules: Optional[List[str]] = None
    barriers: Optional[List[BarrierAssessmentInput]] = None
    evidence_spans: Optional[List[EvidenceSpanInput]] = None
    urgency_score: Optional[int] = None
    potential_consequence: Optional[str] = None
    notes: Optional[str] = None


class AnnotationSubmitRequest(BaseModel):
    """Final submission payload (strict validation of required fields)."""
    sif_potential: SIFPotentialLevel = Field(..., description="Canonical SIF potential level")
    sif_precursor: SIFPrecursorFlag = Field(..., description="Canonical SIF precursor flag")
    primary_hazard: str = Field(..., description="Primary hazard classification")
    secondary_hazards: Optional[List[str]] = Field(default_factory=list)
    activity: str = Field(..., description="Operational activity")
    primary_precursor: str = Field(..., description="Primary precursor category")
    precursor_categories: List[str] = Field(default_factory=list, description="Multi-label precursor categories")
    life_saving_rule: str = Field(..., description="Primary Life-Saving Rule")
    life_saving_rules: List[str] = Field(default_factory=list, description="Life-Saving Rules multi-select")
    barriers: List[BarrierAssessmentInput] = Field(default_factory=list)
    evidence_spans: List[EvidenceSpanInput] = Field(default_factory=list)
    urgency_score: Optional[int] = Field(default=50, ge=0, le=100)
    potential_consequence: Optional[str] = None
    notes: Optional[str] = None


# ------------------------------------------------------------------------------
# Disagreement & Adjudication Schemas
# ------------------------------------------------------------------------------

class DisagreementRead(BaseModel):
    """Field-level discrepancy between paired annotators."""
    id: str
    task_id: str
    report_id: str
    field_name: str
    annotator_a_id: str
    annotator_b_id: str
    annotator_a_name: Optional[str] = None
    annotator_b_name: Optional[str] = None
    annotator_a_value: Any
    annotator_b_value: Any
    status: str
    created_at: datetime


class DisagreementDetail(BaseModel):
    """Full detail view for Lead HSE Adjudicator."""
    task_id: str
    report_id: str
    raw_text: str
    facility_id: str
    location: Optional[str] = None
    activity: Optional[str] = None
    disagreements: List[DisagreementRead]
    submission_a: AnnotationSubmissionRead
    submission_b: AnnotationSubmissionRead


class AdjudicationRequest(BaseModel):
    """Resolution submitted by Lead HSE Expert."""
    resolved_sif_potential: SIFPotentialLevel
    resolved_sif_precursor: SIFPrecursorFlag
    resolved_primary_hazard: str
    resolved_secondary_hazards: Optional[List[str]] = None
    resolved_activity: str
    resolved_primary_precursor: str
    resolved_precursor_categories: Optional[List[str]] = None
    resolved_life_saving_rule: str
    resolved_life_saving_rules: Optional[List[str]] = None
    resolved_barriers: Optional[List[BarrierAssessmentInput]] = None
    resolved_evidence_spans: Optional[List[EvidenceSpanInput]] = None
    adjudication_notes: str = Field(..., min_length=5, description="Expert explanation of resolution")


class AdjudicationRead(BaseModel):
    """Resolved adjudication record."""
    id: str
    task_id: str
    report_id: str
    adjudicator_id: str
    adjudicator_name: Optional[str] = None
    resolved_sif_potential: str
    resolved_sif_precursor: str
    resolved_primary_hazard: str
    resolved_primary_precursor: str
    resolved_life_saving_rule: str
    adjudication_notes: str
    adjudicated_at: datetime


# ------------------------------------------------------------------------------
# Quality & Release Readiness Schemas
# ------------------------------------------------------------------------------

class AnnotationQualityReport(BaseModel):
    """Inter-annotator agreement quality metrics."""
    batch_id: Optional[str] = None
    total_paired_records: int
    unanimous_consensus_count: int
    discrepancy_count: int
    sif_potential_agreement_pct: float
    precursor_category_agreement_pct: float
    life_saving_rule_agreement_pct: float
    primary_hazard_agreement_pct: float
    multilabel_precursor_jaccard: float
    evidence_span_iou: float
    overall_cohens_kappa: float
    unresolved_disagreements_count: int


class ReleaseGateItem(BaseModel):
    """Status of a single release gate."""
    gate_name: str
    title: str
    passed: bool
    severity: str  # CRITICAL, WARNING, INFO
    details: str


class ReleaseReadinessReport(BaseModel):
    """7-gate release audit report."""
    batch_id: Optional[str] = None
    is_release_approved: bool
    total_records: int
    critical_failures: int
    warnings: int
    gates: List[ReleaseGateItem]


class TaxonomyReferenceData(BaseModel):
    """Canonical SIFT taxonomy reference lists for dynamic form population."""
    sif_potential_levels: List[str]
    sif_precursor_flags: List[str]
    precursor_categories: List[str]
    primary_hazards: List[str]
    activity_categories: List[str]
    life_saving_rules: List[str]
    barrier_categories: List[str]
    barrier_status_levels: List[str]
