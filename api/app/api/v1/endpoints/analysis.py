"""AI NLP Analysis endpoints."""

from fastapi import APIRouter, Depends, status
from app.api.deps import get_analysis_service
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import AnalyzeRequest, ReportAnalysisResult

router = APIRouter(tags=["AI Safety Analysis"])


@router.post(
    "/reports/analyze",
    response_model=ReportAnalysisResult,
    status_code=status.HTTP_200_OK,
    summary="Analyze Free-Text Safety Report Narrative",
)
async def analyze_safety_report(
    payload: AnalyzeRequest,
    service: AnalysisService = Depends(get_analysis_service),
) -> ReportAnalysisResult:
    """Execute AI NLP feature extraction, SIF precursor detection, Life-Saving Rule mapping,
    and barrier failure diagnosis on a raw narrative without automatically saving it.
    """
    return await service.analyze_report(payload)
