"""Safety Intelligence and Precursor Pattern Detection endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Body
from app.api.deps import get_intelligence_service
from app.services.intelligence_service import IntelligenceService
from app.schemas.intelligence import (
    PatternRead,
    PatternOverviewKPIs,
    SimilarReportsResponse,
)
from app.utils.filters import PatternFilterParams

router = APIRouter(prefix="/intelligence", tags=["Safety Intelligence & Patterns"])


@router.get(
    "/overview",
    response_model=PatternOverviewKPIs,
    summary="Pattern Intelligence KPI Overview",
)
async def get_pattern_overview(
    service: IntelligenceService = Depends(get_intelligence_service),
) -> PatternOverviewKPIs:
    """Retrieve macro summary of detected precursor patterns across OIL installations."""
    return await service.get_pattern_kpis()


@router.get(
    "/patterns",
    response_model=List[PatternRead],
    summary="List Recurring SIF Precursor Patterns",
)
async def list_patterns(
    category: Optional[str] = Query(default=None, description="Precursor category filter"),
    risk_level: Optional[str] = Query(default=None, description="Risk level (CRITICAL, HIGH, MEDIUM)"),
    facility: Optional[str] = Query(default=None, description="Facility focus"),
    search: Optional[str] = Query(default=None, description="Keyword search"),
    service: IntelligenceService = Depends(get_intelligence_service),
) -> List[PatternRead]:
    """Retrieve recurring cross-site precursor clusters calculated from relational safety data."""
    filters = PatternFilterParams(
        category=category,
        risk_level=risk_level,
        facility=facility,
        search=search,
    )
    return await service.list_patterns(filters)


@router.get(
    "/patterns/{pattern_id}",
    response_model=PatternRead,
    summary="Get Specific Pattern Details",
)
async def get_pattern(
    pattern_id: str,
    service: IntelligenceService = Depends(get_intelligence_service),
) -> PatternRead:
    """Retrieve detailed failure mode and recommended intervention for a precursor pattern."""
    return await service.get_pattern_by_id(pattern_id)


@router.get(
    "/similar-reports/{report_id}",
    response_model=SimilarReportsResponse,
    summary="Find Semantically Similar Historical Reports",
)
async def get_similar_reports(
    report_id: str,
    top_k: int = Query(default=4, ge=1, le=20),
    service: IntelligenceService = Depends(get_intelligence_service),
) -> SimilarReportsResponse:
    """Perform vector similarity search to identify historical reports with matching hazard semantics."""
    return await service.find_similar_reports(report_identifier=report_id, top_k=top_k)


@router.post(
    "/similar-reports",
    response_model=SimilarReportsResponse,
    summary="Find Similar Reports for Arbitrary Text",
)
async def query_similar_reports_by_text(
    query_text: str = Body(..., embed=True, description="Safety narrative text to match"),
    top_k: int = Query(default=4, ge=1, le=20),
    service: IntelligenceService = Depends(get_intelligence_service),
) -> SimilarReportsResponse:
    """Find semantically similar historical safety observations from raw text."""
    return await service.find_similar_reports(query_text=query_text, top_k=top_k)
