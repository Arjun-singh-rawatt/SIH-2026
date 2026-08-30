"""SafetyReport Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.facility import FacilityRead
from app.schemas.barrier import BarrierAssessmentRead
from app.schemas.action import ActionItemRead
from app.utils.enums import ReportType, SIFPotential, SIFPrecursor, ReviewStatus, BarrierStatus


class ReportCreate(BaseModel):
    report_id: Optional[str] = None
    reporter_id: str = Field(default="USR-002")
    reporter_name: Optional[str] = None
    facility_id: str = Field(default="FAC-DIG-02")
    facility_name: Optional[str] = None
    region: Optional[str] = None
    location: str = Field(default="Main Processing Unit")
    raw_report_text: str = Field(..., min_length=5)
    language: str = Field(default="English")
    report_type: str = Field(default=ReportType.NEAR_MISS.value)
    activity: str = Field(default="Maintenance")
    potential_consequence: Optional[str] = None

    # AI assessment fields (if provided by client or automatically run)
    sif_potential: Optional[str] = None
    sif_precursor: Optional[str] = None
    confidence: Optional[float] = None
    urgency_score: Optional[int] = None
    primary_hazard: Optional[str] = None
    precursor_category: Optional[str] = None
    life_saving_rule: Optional[str] = None
    failed_barrier: Optional[str] = None
    barrier_status: Optional[str] = None
    evidence_phrase: Optional[str] = None
    evidence_phrases: Optional[List[str]] = None
    ai_explanation: Optional[str] = None


class ReportUpdate(BaseModel):
    facility_id: Optional[str] = None
    location: Optional[str] = None
    report_type: Optional[str] = None
    activity: Optional[str] = None
    potential_consequence: Optional[str] = None
    review_status: Optional[str] = None
    reviewer_notes: Optional[str] = None
    final_sif_potential: Optional[str] = None
    final_sif_precursor: Optional[str] = None
    final_life_saving_rule: Optional[str] = None
    final_failed_barrier: Optional[str] = None
    final_barrier_status: Optional[str] = None


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_id: str
    reporter_id: str
    facility_id: str
    facility_name: Optional[str] = None
    region: Optional[str] = None
    location: str
    raw_report_text: str
    language: str
    report_type: str
    activity: str
    primary_hazard: str
    precursor_category: str
    potential_consequence: Optional[str] = None

    # AI predictions
    ai_sif_potential: str
    ai_sif_precursor: str
    ai_confidence: float
    ai_urgency_score: int
    ai_life_saving_rule: str
    ai_failed_barrier: Optional[str] = None
    ai_barrier_status: str
    ai_evidence_phrase: Optional[str] = None
    ai_explanation: Optional[str] = None

    # Human review & final results
    review_status: str
    reviewer_id: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    final_sif_potential: Optional[str] = None
    final_sif_precursor: Optional[str] = None
    final_life_saving_rule: Optional[str] = None
    final_failed_barrier: Optional[str] = None
    final_barrier_status: Optional[str] = None

    # Active operational values
    sif_potential: str
    sif_precursor: str
    confidence: float
    urgency_score: int
    life_saving_rule: str
    failed_barrier: str
    barrier_status: str
    evidence_phrase: Optional[str] = None
    evidence_phrases: List[str] = Field(default_factory=list)
    ai_explanation: Optional[str] = None

    created_at: datetime
    updated_at: datetime


class ReportDetail(ReportRead):
    facility: Optional[FacilityRead] = None
    barrier_assessments: List[BarrierAssessmentRead] = Field(default_factory=list)
    actions: List[ActionItemRead] = Field(default_factory=list)
    has_vector_embedding: bool = False


class ReportStats(BaseModel):
    total_count: int
    sif_count: int
    high_urgency_count: int
    pending_review_count: int
    sif_density: float  # percentage
