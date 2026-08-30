"""Canonical Dataset Record Schema for SIFT AI.

Formal JSONL schema models for training, validation, testing,
annotation workflows, and dataset serialization.
Schema Version: 1.0
"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.ai.taxonomy import (
    SIFPotentialLevel,
    SIFPrecursorFlag,
    PrecursorCategory,
    BarrierStatusLevel,
    SafetyBarrierCategory,
)


class DatasetEvidenceSpan(BaseModel):
    """Character-offset grounded evidence span extracted from raw report text."""
    text: str = Field(..., description="Exact substring extracted from the raw narrative")
    start_offset: int = Field(..., ge=0, description="0-indexed start character offset in raw text")
    end_offset: int = Field(..., gt=0, description="0-indexed end character offset in raw text")

    @model_validator(mode="after")
    def validate_offsets(self) -> "DatasetEvidenceSpan":
        if self.end_offset <= self.start_offset:
            raise ValueError(f"end_offset ({self.end_offset}) must be strictly greater than start_offset ({self.start_offset})")
        return self


class DatasetBarrierAssessment(BaseModel):
    """Detailed barrier failure diagnosis."""
    barrier_name: str = Field(..., description="Standardized name of the safety barrier")
    status: BarrierStatusLevel = Field(..., description="Barrier integrity status (FAILED, WEAK, EFFECTIVE, UNKNOWN)")
    barrier_type: SafetyBarrierCategory = Field(
        default=SafetyBarrierCategory.ENGINEERING,
        description="Hierarchy of controls barrier category"
    )
    description: Optional[str] = Field(default=None, description="Contextual notes on barrier failure mode")


class DatasetContext(BaseModel):
    """Operational and geographic metadata for the field safety report."""
    facility_id: str = Field(..., description="Operational facility identifier (e.g. FAC-DIG-02)")
    facility_name: Optional[str] = Field(default=None, description="Full human-readable facility name")
    region: Optional[str] = Field(default="Upper Assam Basin", description="OIL operating region/basin")
    location: Optional[str] = Field(default=None, description="Specific skid, header, or plant unit")
    activity: str = Field(default="Maintenance", description="Operational activity being executed")


class DatasetLabels(BaseModel):
    """Ground truth annotations for all 13 AI safety intelligence tasks."""
    sif_potential: SIFPotentialLevel = Field(..., description="Ground truth SIF potential level")
    sif_precursor: SIFPrecursorFlag = Field(..., description="High-energy hazard without direct barrier")
    
    primary_precursor: PrecursorCategory = Field(..., description="Dominant precursor category")
    secondary_precursors: List[PrecursorCategory] = Field(
        default_factory=list,
        description="Additional simultaneous precursor mechanisms (multi-label support)"
    )

    primary_hazard: str = Field(..., description="Standardized primary physical/chemical hazard")
    secondary_hazards: List[str] = Field(default_factory=list, description="Additional active hazards")

    life_saving_rule: str = Field(..., description="Primary mapped IOGP Life-Saving Rule")
    barriers: List[DatasetBarrierAssessment] = Field(
        default_factory=list,
        description="Assessed safety barrier integrity states"
    )

    evidence_spans: List[DatasetEvidenceSpan] = Field(
        default_factory=list,
        description="Grounded evidence spans extracted from raw text"
    )

    urgency_score: int = Field(..., ge=0, le=100, description="HSE urgency risk index 0-100")
    potential_consequence: Optional[str] = Field(
        default=None,
        description="Projected worst-case realistic physical consequence"
    )
    ai_explanation: Optional[str] = Field(
        default=None,
        description="Concise rationale explaining the safety assessment"
    )


class DatasetAnnotationMetadata(BaseModel):
    """Auditability and provenance tracking for human annotation."""
    annotator_id: str = Field(..., description="Identifier of primary human annotator")
    adjudicator_id: Optional[str] = Field(default=None, description="Identifier of resolving lead safety expert")
    review_status: str = Field(
        default="ADJUDICATED",
        description="Annotation stage: UNANNOTATED | SINGLE_ANNOTATED | DOUBLE_ANNOTATED | ADJUDICATED"
    )
    taxonomy_version: str = Field(default="1.0", description="Taxonomy version active during annotation")
    annotated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of label finalization")
    disagreement_notes: Optional[str] = Field(default=None, description="Notes resolving annotator divergence")


class DatasetRecord(BaseModel):
    """Canonical SIFT JSONL Dataset Record."""
    schema_version: str = Field(default="1.0", description="Dataset schema version")
    report_id: str = Field(..., description="Unique safety observation ID (e.g. SIF-2026-00124)")
    split: Optional[str] = Field(
        default=None,
        description="Dataset split assignment: TRAIN | VALIDATION | TEST"
    )
    raw_text: str = Field(..., min_length=5, description="Full unedited field report narrative")
    report_type: str = Field(..., description="Observation type: Near Miss | Unsafe Act | Unsafe Condition | Incident")
    
    context: DatasetContext
    labels: DatasetLabels
    annotation: DatasetAnnotationMetadata

    @model_validator(mode="after")
    def validate_evidence_spans(self) -> "DatasetRecord":
        """Validate that all evidence spans are exact substrings of the raw report text."""
        raw = self.raw_text
        for span in self.labels.evidence_spans:
            if span.end_offset > len(raw):
                raise ValueError(
                    f"Evidence span end_offset {span.end_offset} exceeds raw_text length {len(raw)}"
                )
            extracted = raw[span.start_offset:span.end_offset]
            if extracted != span.text:
                raise ValueError(
                    f"Span text mismatch: expected '{span.text}', but found '{extracted}' at [{span.start_offset}:{span.end_offset}]"
                )
        return self
