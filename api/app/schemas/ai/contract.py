"""Model Inference & Serving Contracts for SIFT AI Pipeline.

Formal request and response schemas for AI inference models,
calibration artifacts, and explainability payloads.
Contract Version: 1.0
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from app.schemas.ai.taxonomy import (
    SIFPotentialLevel,
    SIFPrecursorFlag,
    PrecursorCategory,
    BarrierStatusLevel,
)
from app.schemas.ai.dataset import DatasetEvidenceSpan, DatasetBarrierAssessment


class ModelInferenceRequest(BaseModel):
    """Payload sent to AI inference service or model runner."""
    report_text: str = Field(..., min_length=5, description="Raw safety narrative to analyze")
    report_type: Optional[str] = Field(default="Near Miss", description="Near Miss | Unsafe Act | Unsafe Condition | Incident")
    facility_id: Optional[str] = Field(default=None, description="Operational facility ID for localized context")
    location: Optional[str] = Field(default=None, description="Skid or plant section")
    activity: Optional[str] = Field(default="Maintenance", description="Operational task context")


class ModelConfidenceBreakdown(BaseModel):
    """Calibrated confidence scores across model prediction heads."""
    overall_confidence: float = Field(..., ge=0.0, le=100.0, description="Aggregated pipeline confidence percentage")
    sif_potential_confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated posterior for SIF Potential")
    precursor_confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated posterior for Precursor Category")
    is_calibrated: bool = Field(default=False, description="Whether temperature scaling / Platt scaling was applied")
    calibration_method: Optional[str] = Field(default=None, description="e.g. TemperatureScaling, IsotonicRegression")


class UrgencyScoreBreakdown(BaseModel):
    """Transparent heuristic scoring weights for the calculated urgency score."""
    final_score: int = Field(..., ge=0, le=100, description="Calculated urgency index (0-100)")
    sif_potential_weight: float = Field(..., description="Contribution from SIF Potential tier (0-40)")
    hazard_severity_weight: float = Field(..., description="Contribution from primary hazard severity (0-25)")
    barrier_failure_weight: float = Field(..., description="Contribution from barrier failure state (0-20)")
    exposure_activity_weight: float = Field(..., description="Contribution from activity risk index (0-15)")
    scoring_method: str = Field(default="BASELINE_HEURISTIC_V1", description="Scoring formula version")


class ModelInferenceResult(BaseModel):
    """Standardized AI Pipeline output returned from AI Provider to FastAPI services."""
    model_version: str = Field(..., description="Model identifier and version (e.g. sift-roberta-v1.2)")
    
    # Classification Task Outputs
    sif_potential: SIFPotentialLevel = Field(..., description="Predicted SIF Potential")
    sif_precursor: SIFPrecursorFlag = Field(..., description="SIF Precursor Flag")
    primary_precursor: PrecursorCategory = Field(..., description="Dominant SIF Precursor Category")
    secondary_precursors: List[PrecursorCategory] = Field(default_factory=list, description="Additional multi-label precursors")
    
    # Extraction & Mapping Outputs
    primary_hazard: str = Field(..., description="Identified primary industrial hazard")
    activity: str = Field(..., description="Operational activity performed")
    life_saving_rule: str = Field(..., description="Mapped IOGP Life-Saving Rule")
    barriers: List[DatasetBarrierAssessment] = Field(default_factory=list, description="Diagnosed barrier failures")
    
    # Grounded Evidence & Explainability
    evidence_spans: List[DatasetEvidenceSpan] = Field(default_factory=list, description="Extracted trigger phrases with offsets")
    primary_evidence_phrase: str = Field(..., description="Concatenated or primary evidence snippet")
    ai_explanation: str = Field(..., description="Concise rationale grounded in the observation narrative")
    potential_consequence: Optional[str] = Field(default=None, description="Projected consequence")
    
    # Confidence & Urgency
    confidence: float = Field(..., ge=0.0, le=100.0, description="Model confidence 0-100%")
    confidence_breakdown: Optional[ModelConfidenceBreakdown] = None
    urgency_score: int = Field(..., ge=0, le=100, description="Calculated urgency index 0-100")
    urgency_breakdown: Optional[UrgencyScoreBreakdown] = None
