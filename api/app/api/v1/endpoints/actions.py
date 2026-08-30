"""Corrective & Preventative Action (CAPA) endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.api.deps import get_action_service
from app.services.action_service import ActionService
from app.schemas.action import (
    ActionItemRead,
    ActionItemCreate,
    ActionItemUpdate,
    ActionStatsResponse,
)
from app.schemas.common import GenericSuccessResponse
from app.utils.filters import ActionFilterParams
from app.utils.pagination import PageParams, PaginatedResponse

router = APIRouter(prefix="/actions", tags=["CAPA Action Items"])


@router.get(
    "",
    response_model=PaginatedResponse[ActionItemRead],
    summary="List & Filter Action Items",
)
async def list_actions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: Optional[str] = Query(default=None, description="Search keyword"),
    status: Optional[str] = Query(default=None, description="Status (Open, In Progress, Completed, Overdue)"),
    priority: Optional[str] = Query(default=None, description="Priority (CRITICAL, HIGH, MEDIUM, LOW)"),
    facility_id: Optional[str] = Query(default=None, description="Facility ID filter"),
    assigned_to: Optional[str] = Query(default=None, description="Assignee User ID filter"),
    report_id: Optional[str] = Query(default=None, description="Linked Report ID filter"),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    service: ActionService = Depends(get_action_service),
) -> PaginatedResponse[ActionItemRead]:
    """Retrieve paginated CAPA actions with multi-dimensional status and assignee filtering."""
    filters = ActionFilterParams(
        search=search,
        status=status,
        priority=priority,
        facility_id=facility_id,
        assigned_to=assigned_to,
        report_id=report_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    page_params = PageParams(page=page, page_size=page_size)
    return await service.list_actions(filters, page_params)


@router.get(
    "/stats",
    response_model=ActionStatsResponse,
    summary="Action Items Status Counters",
)
async def get_action_stats(
    service: ActionService = Depends(get_action_service),
) -> ActionStatsResponse:
    """Returns counts of total, open, in progress, completed, and overdue action items."""
    return await service.get_action_stats()


@router.get(
    "/{action_id}",
    response_model=ActionItemRead,
    summary="Get Action Item Details",
)
async def get_action(
    action_id: str,
    service: ActionService = Depends(get_action_service),
) -> ActionItemRead:
    """Retrieve details for a specific corrective action."""
    return await service.get_action_by_id(action_id)


@router.post(
    "",
    response_model=ActionItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create & Assign New Action Item",
)
async def create_action(
    payload: ActionItemCreate,
    service: ActionService = Depends(get_action_service),
) -> ActionItemRead:
    """Assign a new corrective or preventative safety barrier remediation."""
    return await service.create_action(payload)


@router.patch(
    "/{action_id}",
    response_model=ActionItemRead,
    summary="Update Action Item Status / Fields",
)
async def update_action(
    action_id: str,
    payload: ActionItemUpdate,
    service: ActionService = Depends(get_action_service),
) -> ActionItemRead:
    """Update action item status (e.g. In Progress -> Completed), due date, or priority."""
    return await service.update_action(action_id, payload)


@router.delete(
    "/{action_id}",
    response_model=GenericSuccessResponse,
    summary="Delete Action Item",
)
async def delete_action(
    action_id: str,
    service: ActionService = Depends(get_action_service),
) -> GenericSuccessResponse:
    """Delete a CAPA action item."""
    await service.delete_action(action_id)
    return GenericSuccessResponse(message=f"Action item #{action_id} deleted successfully.")
