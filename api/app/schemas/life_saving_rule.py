"""IOGP Life-Saving Rules schemas."""

from typing import List, Optional, Any
from pydantic import BaseModel, Field


class LifeSavingRuleRead(BaseModel):
    id: str
    name: str
    category: str
    short_description: str
    full_description: str
    icon_name: str
    color: str
    bg_color: str
    risk_level: str
    total_reports: int
    sif_reports: int
    sif_percentage: float
    trend: str
    trend_direction: str
    top_activity: str
    top_facility: str
    key_requirements: List[str]


class LifeSavingRuleDetail(LifeSavingRuleRead):
    associated_reports: List[Any] = Field(default_factory=list)
