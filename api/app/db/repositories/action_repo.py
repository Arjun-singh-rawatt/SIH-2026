"""ActionItem repository."""

from typing import Optional, Sequence, Tuple, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.action_item import ActionItem
from app.db.models.safety_report import SafetyReport
from app.db.models.user import User
from app.db.models.facility import Facility
from app.db.repositories.base_repo import BaseRepository
from app.utils.filters import ActionFilterParams
from app.utils.pagination import PageParams
from app.utils.enums import ActionStatus


class ActionRepository(BaseRepository[ActionItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(ActionItem, db)

    async def get_by_identifier(self, identifier: str) -> Optional[ActionItem]:
        stmt = (
            select(ActionItem)
            .options(
                joinedload(ActionItem.report),
                joinedload(ActionItem.assignee),
                joinedload(ActionItem.facility),
            )
            .where(
                or_(
                    ActionItem.id == identifier,
                    ActionItem.action_id == identifier,
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def filter_actions(
        self,
        filters: ActionFilterParams,
        page_params: PageParams,
    ) -> Tuple[Sequence[ActionItem], int]:
        query = (
            select(ActionItem)
            .join(ActionItem.facility, isouter=True)
            .join(ActionItem.assignee, isouter=True)
            .join(ActionItem.report, isouter=True)
        )
        conditions = []

        if filters.search and filters.search.strip():
            q = f"%{filters.search.strip()}%"
            conditions.append(
                or_(
                    ActionItem.action_id.ilike(q),
                    ActionItem.description.ilike(q),
                    ActionItem.action_type.ilike(q),
                    ActionItem.report_id.ilike(q),
                    User.name.ilike(q),
                    Facility.name.ilike(q),
                    Facility.short_name.ilike(q),
                )
            )

        if filters.status and filters.status != "ALL":
            conditions.append(ActionItem.status == filters.status)

        if filters.priority and filters.priority != "ALL":
            conditions.append(ActionItem.priority == filters.priority)

        if filters.facility_id and filters.facility_id != "ALL":
            conditions.append(ActionItem.facility_id == filters.facility_id)

        if filters.assigned_to and filters.assigned_to != "ALL":
            conditions.append(ActionItem.assigned_to == filters.assigned_to)

        if filters.report_id and filters.report_id != "ALL":
            conditions.append(ActionItem.report_id == filters.report_id)

        if conditions:
            query = query.where(and_(*conditions))

        # Total count
        count_stmt = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        # Sorting
        sort_col = getattr(ActionItem, filters.sort_by, ActionItem.created_at)
        if filters.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        # Relations
        query = query.options(
            joinedload(ActionItem.report),
            joinedload(ActionItem.assignee),
            joinedload(ActionItem.facility),
        )

        query = query.offset(page_params.offset).limit(page_params.limit)
        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_actions_for_report(self, report_id: str) -> Sequence[ActionItem]:
        stmt = (
            select(ActionItem)
            .options(
                joinedload(ActionItem.assignee),
                joinedload(ActionItem.facility),
            )
            .where(ActionItem.report_id == report_id)
            .order_by(desc(ActionItem.created_at))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_action_stats(self) -> Dict[str, int]:
        total = await self.count()
        
        async def count_status(status_val: str) -> int:
            stmt = select(func.count(ActionItem.id)).where(ActionItem.status == status_val)
            return (await self.db.execute(stmt)).scalar_one()

        open_cnt = await count_status(ActionStatus.OPEN.value)
        in_prog_cnt = await count_status(ActionStatus.IN_PROGRESS.value)
        comp_cnt = await count_status(ActionStatus.COMPLETED.value)
        overdue_cnt = await count_status(ActionStatus.OVERDUE.value)

        return {
            "total": total,
            "open": open_cnt,
            "in_progress": in_prog_cnt,
            "completed": comp_cnt,
            "overdue": overdue_cnt,
        }

    async def generate_next_action_id(self) -> str:
        year = datetime.now(timezone.utc).year
        stmt = select(func.count(ActionItem.id))
        count = (await self.db.execute(stmt)).scalar_one()
        return f"ACT-{year}-{str(count + 1).zfill(3)}"
