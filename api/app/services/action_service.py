"""ActionItem and CAPA tracking service."""

from typing import Optional, List
from datetime import datetime, timezone
from app.db.repositories.action_repo import ActionRepository
from app.db.repositories.report_repo import ReportRepository
from app.db.repositories.user_repo import UserRepository
from app.db.repositories.facility_repo import FacilityRepository
from app.db.models.action_item import ActionItem
from app.schemas.action import (
    ActionItemRead,
    ActionItemCreate,
    ActionItemUpdate,
    ActionStatsResponse,
)
from app.utils.filters import ActionFilterParams
from app.utils.pagination import PageParams, PaginatedResponse
from app.utils.enums import ActionStatus
from app.core.errors import ActionNotFoundException


class ActionService:
    def __init__(
        self,
        action_repo: ActionRepository,
        report_repo: ReportRepository,
        user_repo: UserRepository,
        facility_repo: FacilityRepository,
    ):
        self.repo = action_repo
        self.report_repo = report_repo
        self.user_repo = user_repo
        self.facility_repo = facility_repo

    def _to_read_schema(self, a: ActionItem) -> ActionItemRead:
        rep_title = a.report.ai_primary_hazard if a.report else a.action_type
        assignee_name = a.assignee.name if a.assignee else a.assigned_to
        assignee_role = a.assignee.role if a.assignee else None
        fac_name = a.facility.short_name if a.facility else a.facility_id

        return ActionItemRead(
            id=a.id,
            action_id=a.action_id,
            report_id=a.report_id,
            report_title=rep_title,
            assigned_to=a.assigned_to,
            assignee_name=assignee_name,
            assignee_role=assignee_role,
            facility_id=a.facility_id,
            facility_name=fac_name,
            action_type=a.action_type,
            description=a.description,
            priority=a.priority,
            status=a.status,
            due_date=a.due_date,
            completed_at=a.completed_at,
            created_at=a.created_at,
            updated_at=a.updated_at,
        )

    async def list_actions(
        self,
        filters: ActionFilterParams,
        page_params: PageParams,
    ) -> PaginatedResponse[ActionItemRead]:
        actions, total = await self.repo.filter_actions(filters, page_params)
        items = [self._to_read_schema(a) for a in actions]
        return PaginatedResponse.create(items=items, total=total, params=page_params)

    async def get_action_by_id(self, identifier: str) -> ActionItemRead:
        act = await self.repo.get_by_identifier(identifier)
        if not act:
            raise ActionNotFoundException(identifier)
        return self._to_read_schema(act)

    async def get_actions_for_report(self, report_id: str) -> List[ActionItemRead]:
        actions = await self.repo.get_actions_for_report(report_id)
        return [self._to_read_schema(a) for a in actions]

    async def create_action(self, payload: ActionItemCreate) -> ActionItemRead:
        # Generate action_id
        action_id = await self.repo.generate_next_action_id()

        action = ActionItem(
            action_id=action_id,
            report_id=payload.report_id,
            assigned_to=payload.assigned_to,
            facility_id=payload.facility_id,
            action_type=payload.action_type,
            description=payload.description,
            priority=payload.priority,
            status=ActionStatus.OPEN.value,
            due_date=payload.due_date,
        )

        created = await self.repo.create(action)
        return await self.get_action_by_id(created.action_id)

    async def update_action(self, identifier: str, payload: ActionItemUpdate) -> ActionItemRead:
        act = await self.repo.get_by_identifier(identifier)
        if not act:
            raise ActionNotFoundException(identifier)

        update_dict = payload.model_dump(exclude_unset=True)
        if "status" in update_dict:
            if update_dict["status"] == ActionStatus.COMPLETED.value and not act.completed_at:
                act.completed_at = datetime.now(timezone.utc)
            elif update_dict["status"] != ActionStatus.COMPLETED.value:
                act.completed_at = None

        for k, v in update_dict.items():
            setattr(act, k, v)

        updated = await self.repo.update(act)
        return await self.get_action_by_id(updated.action_id)

    async def delete_action(self, identifier: str) -> None:
        act = await self.repo.get_by_identifier(identifier)
        if not act:
            raise ActionNotFoundException(identifier)
        await self.repo.delete(act)

    async def get_action_stats(self) -> ActionStatsResponse:
        stats = await self.repo.get_action_stats()
        return ActionStatsResponse(**stats)
