"""Barrier Assessment Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.utils.enums import BarrierStatus


class BarrierAssessmentBase(BaseModel):
    failed_barrier: str = Field(..., description="Name of the failed or weakened safety barrier")
    barrier_status: str = Field(default=BarrierStatus.FAILED.value)
    barrier_type: str = Field(default="Physical / Procedural")
    life_saving_rule: Optional[str] = None
    description: Optional[str] = None


class BarrierAssessmentCreate(BarrierAssessmentBase):
    report_id: Optional[str] = None


class BarrierAssessmentRead(BarrierAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    report_id: str
    created_at: datetime
    updated_at: datetime
