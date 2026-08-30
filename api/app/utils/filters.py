"""Filter parameter models for queries."""

from typing import Optional
from pydantic import BaseModel
from app.utils.enums import SIFPotential, ReportType, ReviewStatus


class ReportFilterParams(BaseModel):
    search: Optional[str] = None
    facility_id: Optional[str] = None
    region: Optional[str] = None
    report_type: Optional[str] = None
    sif_potential: Optional[str] = None
    urgency_level: Optional[str] = None  # HIGH, MEDIUM, LOW or threshold
    life_saving_rule: Optional[str] = None
    review_status: Optional[str] = None
    activity: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"  # asc, desc


class ActionFilterParams(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    facility_id: Optional[str] = None
    assigned_to: Optional[str] = None
    report_id: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class PatternFilterParams(BaseModel):
    search: Optional[str] = None
    category: Optional[str] = None
    risk_level: Optional[str] = None
    facility: Optional[str] = None
