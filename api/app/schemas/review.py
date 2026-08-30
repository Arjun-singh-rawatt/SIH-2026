"""Human-in-the-loop Review Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.utils.enums import ReviewStatus, SIFPotential, SIFPrecursor


class ReviewSubmitRequest(BaseModel):
    action: str = Field(..., description="Action: APPROVE, MODIFY, MARK_NON_SIF, ESCALATE")
    reviewer_id: Optional[str] = Field(default="USR-001")
    reviewer_name: Optional[str] = Field(default="Alok Sharma")
    reviewer_notes: Optional[str] = None
    
    # Modifications if action == "MODIFY" or "MARK_NON_SIF"
    final_sif_potential: Optional[str] = None
    final_sif_precursor: Optional[str] = None
    final_life_saving_rule: Optional[str] = None
    final_failed_barrier: Optional[str] = None
    final_barrier_status: Optional[str] = None


class ReviewQueueSummary(BaseModel):
    pending_count: int
    critical_count: int
    low_confidence_count: int
    total_count: int
