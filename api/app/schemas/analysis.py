"""AI Analysis request and structured validated response schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.utils.enums import SIFPotential, SIFPrecursor, BarrierStatus, ReportType


class AnalyzeRequest(BaseModel):
    report_text: str = Field(..., min_length=5, description="Raw safety report narrative")
    report_type: Optional[str] = Field(default=ReportType.NEAR_MISS.value)
    facility_id: Optional[str] = Field(default="FAC-DIG-02")
    facility_name: Optional[str] = None
    region: Optional[str] = None
    location: Optional[str] = Field(default="Main Processing Section")
    activity: Optional[str] = Field(default="Maintenance")


class ReportAnalysisResult(BaseModel):
    sif_potential: str = Field(..., description="SIF Potential category (CRITICAL, HIGH, MEDIUM, LOW, NON-SIF)")
    sif_precursor: str = Field(default=SIFPrecursor.YES.value, description="SIF Precursor flag (YES/NO/POTENTIAL)")
    confidence: float = Field(..., ge=0.0, le=100.0, description="AI classification confidence score 0-100%")
    urgency_score: int = Field(..., ge=0, le=100, description="HSE urgency risk index 0-100")
    precursor_category: str = Field(..., description="Dominant precursor taxonomy category")
    activity: str = Field(..., description="Operational activity performed")
    primary_hazard: str = Field(..., description="Extracted primary industrial hazard")
    life_saving_rule: str = Field(..., description="Mapped IOGP Life-Saving Rule")
    failed_barrier: str = Field(..., description="Diagnosed failed or degraded barrier")
    barrier_status: str = Field(default=BarrierStatus.FAILED.value)
    potential_consequence: Optional[str] = Field(default=None, description="Projected catastrophic consequence")
    evidence_phrase: str = Field(..., description="Key extracted evidence phrase from raw report")
    evidence_phrases: List[str] = Field(default_factory=list, description="All extracted trigger phrases")
    ai_explanation: str = Field(..., description="Clear rationale explaining the SIF potential assessment")
