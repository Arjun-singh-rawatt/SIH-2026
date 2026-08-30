"""Human-in-the-loop Review Queue and sign-off endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_review_service
from app.services.review_service import ReviewService
from app.schemas.review import ReviewSubmitRequest, ReviewQueueSummary
from app.schemas.report import ReportRead, ReportDetail
from app.utils.pagination import PageParams, PaginatedResponse

router = APIRouter(tags=["Human-in-the-loop Review"])


@router.get(
    "/reviews/queue",
    response_model=PaginatedResponse[ReportRead],
    summary="List Human Review Queue Items",
)
async def get_review_queue(
    tab: str = Query(default="PENDING", description="Queue tab: PENDING, CRITICAL, LOW_CONF, ALL"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
) -> PaginatedResponse[ReportRead]:
    """Retrieve safety reports queued for human HSE expert triage and sign-off."""
    page_params = PageParams(page=page, page_size=page_size)
    return await service.get_queue(tab=tab, page_params=page_params)


@router.get(
    "/reviews/summary",
    response_model=ReviewQueueSummary,
    summary="Review Queue Status Counters",
)
async def get_review_queue_summary(
    service: ReviewService = Depends(get_review_service),
) -> ReviewQueueSummary:
    """Returns counts of pending, critical SIF, and low-confidence reports awaiting triage."""
    return await service.get_queue_summary()


@router.post(
    "/reports/{report_id}/review",
    response_model=ReportDetail,
    status_code=status.HTTP_200_OK,
    summary="Submit Human Review Sign-Off",
)
async def submit_report_review(
    report_id: str,
    payload: ReviewSubmitRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReportDetail:
    """Submit human HSE validation, approval, or re-classification. Preserves original AI prediction."""
    return await service.submit_review(report_id, payload)


@router.patch(
    "/reports/{report_id}/review",
    response_model=ReportDetail,
    summary="Update Review Sign-Off",
)
async def update_report_review(
    report_id: str,
    payload: ReviewSubmitRequest,
    service: ReviewService = Depends(get_review_service),
) -> ReportDetail:
    """Modify an existing human review sign-off."""
    return await service.submit_review(report_id, payload)
