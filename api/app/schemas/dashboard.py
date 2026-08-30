"""Executive Dashboard schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DashboardSummary(BaseModel):
    total_reports: int
    sif_reports: int
    sif_density: float  # %
    high_urgency_reports: int
    open_actions: int


class TrendPoint(BaseModel):
    month: str
    total_reports: int
    sif_reports: int
    high_urgency: int


class PrecursorDistPoint(BaseModel):
    category: str
    count: int
    sif_count: int
    percentage: float


class FacilityRankingPoint(BaseModel):
    facility_id: str
    facility_name: str
    short_name: str
    region: str
    total_reports: int
    sif_reports: int
    sif_density: float
    risk_level: str


class ActivityRankingPoint(BaseModel):
    activity: str
    total_reports: int
    sif_reports: int
    sif_density: float


class BarrierFailurePoint(BaseModel):
    barrier: str
    count: int
    percentage: float


class PriorityAttentionItem(BaseModel):
    report_id: str
    facility_name: str
    primary_hazard: str
    life_saving_rule: str
    urgency_score: int
    sif_potential: str
    created_at: datetime
    review_status: str


class DashboardOverview(BaseModel):
    summary: DashboardSummary
    trend: List[TrendPoint]
    precursor_distribution: List[PrecursorDistPoint]
    facility_ranking: List[FacilityRankingPoint]
    activity_ranking: List[ActivityRankingPoint]
    barrier_failures: List[BarrierFailurePoint]
    priority_attention: List[PriorityAttentionItem]
