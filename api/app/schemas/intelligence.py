"""Safety Intelligence & Pattern Detection schemas."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PatternRead(BaseModel):
    pattern_id: str
    title: str
    category: str
    occurrences: int
    sif_density: float  # %
    risk_level: str
    trend: str
    trend_direction: str  # up, down
    affected_facilities: List[str]
    affected_activities: List[str]
    common_barrier_failure: str
    life_saving_rule: str
    primary_hazard: str
    description: str
    recommended_intervention: str
    sample_report_ids: List[str]


class PatternOverviewKPIs(BaseModel):
    total_patterns: int
    critical_patterns: int
    affected_facilities_count: int
    dominant_precursor: str


class SimilarReportMatch(BaseModel):
    report_id: str
    similarity: float
    precursor_category: str
    facility_name: str
    primary_hazard: str
    life_saving_rule: str
    sif_potential: str
    raw_snippet: Optional[str] = None


class SimilarReportsResponse(BaseModel):
    query_report_id: Optional[str] = None
    query_text: Optional[str] = None
    total_matches: int
    matches: List[SimilarReportMatch]
