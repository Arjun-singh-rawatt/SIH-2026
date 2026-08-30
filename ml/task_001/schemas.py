"""SIFT TASK-001 Prediction & Data Contracts.

Defines standardized Pydantic models for model outputs, confidence scores,
and inference prediction schemas.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class SIFScoreBreakdown(BaseModel):
    """Raw decision function scores or uncalibrated probabilities per SIF class."""
    scores: Dict[str, float] = Field(default_factory=dict)
    score_type: str = Field(default="decision_score", description="'decision_score' or 'uncalibrated_probability'")


class SIFClassificationPrediction(BaseModel):
    """Canonical model inference output for TASK-001 (SIF Potential)."""
    task: str = "TASK-001"
    model_version: str
    predicted_sif_potential: str = Field(..., description="Predicted SIF Potential (CRITICAL, HIGH, MEDIUM, LOW, NON-SIF)")
    confidence: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Confidence or highest score scaled to 0-100")
    decision_scores: SIFScoreBreakdown
    inference_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
