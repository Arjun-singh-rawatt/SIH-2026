"""Safety Reports CRUD and exploration endpoints."""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_report_service, get_action_service
from app.services.report_service import ReportService
from app.services.action_service import ActionService
from app.schemas.report import ReportRead, ReportDetail, ReportCreate, ReportUpdate, ReportStats
from app.schemas.action import ActionItemRead
from app.schemas.common import GenericSuccessResponse
from app.utils.filters import ReportFilterParams
from app.utils.pagination import PageParams, PaginatedResponse

router = APIRouter(prefix="/reports", tags=["Safety Reports"])


@router.get("", response_model=PaginatedResponse[ReportRead], summary="List & Filter Safety Reports")
async def list_reports(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(default=None, description="Search keyword"),
    facility_id: Optional[str] = Query(default=None, description="Facility ID (e.g. FAC-DUL-01)"),
    region: Optional[str] = Query(default=None, description="Operational basin/region"),
    report_type: Optional[str] = Query(default=None, description="Report type (Unsafe Act, Near Miss, etc.)"),
    sif_potential: Optional[str] = Query(default=None, description="SIF potential (CRITICAL, HIGH, MEDIUM, LOW, NON-SIF)"),
    urgency_level: Optional[str] = Query(default=None, description="Urgency index (CRITICAL, HIGH, MEDIUM, LOW)"),
    life_saving_rule: Optional[str] = Query(default=None, description="Life-Saving Rule filter"),
    review_status: Optional[str] = Query(default=None, description="Review status (PENDING, APPROVED, MODIFIED)"),
    activity: Optional[str] = Query(default=None, description="Activity filter"),
    sort_by: str = Query(default="created_at", description="Field to sort by"),
    sort_order: str = Query(default="desc", description="Sort direction (asc, desc)"),
    service: ReportService = Depends(get_report_service),
) -> PaginatedResponse[ReportRead]:
    """Retrieve paginated list of field safety observations with multi-attribute filtering."""
    filters = ReportFilterParams(
        search=search,
        facility_id=facility_id,
        region=region,
        report_type=report_type,
        sif_potential=sif_potential,
        urgency_level=urgency_level,
        life_saving_rule=life_saving_rule,
        review_status=review_status,
        activity=activity,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    page_params = PageParams(page=page, page_size=page_size)
    return await service.list_reports(filters, page_params)


@router.get("/stats", response_model=ReportStats, summary="Safety Reports Aggregate Statistics")
async def get_report_stats(
    service: ReportService = Depends(get_report_service),
) -> ReportStats:
    """Returns high-level report counts, SIF exposure totals, and density percentages."""
    return await service.get_report_stats()


@router.get("/{report_id}", response_model=ReportDetail, summary="Get Safety Report Details")
async def get_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    """Retrieve full details of a specific safety observation including AI analysis and human review."""
    return await service.get_report_by_id(report_id)


@router.post("", response_model=ReportDetail, status_code=status.HTTP_201_CREATED, summary="Create Safety Report")
async def create_report(
    payload: ReportCreate,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    """Ingest a new safety observation, execute automated AI classification, and store."""
    return await service.create_report(payload)


@router.patch("/{report_id}", response_model=ReportDetail, summary="Update Safety Report")
async def update_report(
    report_id: str,
    payload: ReportUpdate,
    service: ReportService = Depends(get_report_service),
) -> ReportDetail:
    """Update fields on an existing safety report."""
    return await service.update_report(report_id, payload)


@router.delete("/{report_id}", response_model=GenericSuccessResponse, summary="Delete Safety Report")
async def delete_report(
    report_id: str,
    service: ReportService = Depends(get_report_service),
) -> GenericSuccessResponse:
    """Permanently delete a safety report and its vector index reference."""
    await service.delete_report(report_id)
    return GenericSuccessResponse(message=f"Report #{report_id} deleted successfully.")


@router.get("/{report_id}/actions", response_model=List[ActionItemRead], summary="Get Actions for Report")
async def get_report_actions(
    report_id: str,
    action_service: ActionService = Depends(get_action_service),
) -> List[ActionItemRead]:
    """List all CAPA action items assigned to this safety observation."""
    return await action_service.get_actions_for_report(report_id)
