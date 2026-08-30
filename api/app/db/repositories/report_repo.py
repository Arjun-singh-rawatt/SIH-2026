"""SafetyReport repository with filtering, aggregation, and query optimizations."""

from typing import Optional, List, Tuple, Sequence
from datetime import datetime, timezone
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.safety_report import SafetyReport
from app.db.models.facility import Facility
from app.db.models.barrier_assessment import BarrierAssessment
from app.db.models.action_item import ActionItem
from app.db.models.vector_reference import ReportVectorReference
from app.db.repositories.base_repo import BaseRepository
from app.utils.filters import ReportFilterParams
from app.utils.pagination import PageParams
from app.utils.enums import ReviewStatus, SIFPotential


class ReportRepository(BaseRepository[SafetyReport]):
    def __init__(self, db: AsyncSession):
        super().__init__(SafetyReport, db)

    async def get_by_identifier(self, identifier: str) -> Optional[SafetyReport]:
        """Find report by either database UUID or business report_id (e.g. SIF-2026-00124)."""
        stmt = (
            select(SafetyReport)
            .options(
                joinedload(SafetyReport.facility),
                joinedload(SafetyReport.reporter),
                selectinload(SafetyReport.barrier_assessments),
                selectinload(SafetyReport.actions),
                joinedload(SafetyReport.vector_reference),
            )
            .where(
                or_(
                    SafetyReport.id == identifier,
                    SafetyReport.report_id == identifier,
                )
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def filter_reports(
        self,
        filters: ReportFilterParams,
        page_params: PageParams,
    ) -> Tuple[Sequence[SafetyReport], int]:
        """Execute parameterized filter query with total count and pagination."""
        query = select(SafetyReport).join(SafetyReport.facility, isouter=True)
        conditions = []

        # Free-text Search
        if filters.search and filters.search.strip():
            q = f"%{filters.search.strip()}%"
            conditions.append(
                or_(
                    SafetyReport.report_id.ilike(q),
                    SafetyReport.raw_report_text.ilike(q),
                    SafetyReport.ai_primary_hazard.ilike(q),
                    SafetyReport.activity.ilike(q),
                    SafetyReport.ai_life_saving_rule.ilike(q),
                    SafetyReport.location.ilike(q),
                    Facility.name.ilike(q),
                    Facility.short_name.ilike(q),
                )
            )

        # Exact / Parametric Filters
        if filters.facility_id and filters.facility_id != "ALL":
            conditions.append(SafetyReport.facility_id == filters.facility_id)

        if filters.region and filters.region != "ALL":
            conditions.append(Facility.region == filters.region)

        if filters.report_type and filters.report_type != "ALL":
            conditions.append(SafetyReport.report_type == filters.report_type)

        if filters.sif_potential and filters.sif_potential != "ALL":
            conditions.append(
                or_(
                    and_(SafetyReport.final_sif_potential.isnot(None), SafetyReport.final_sif_potential == filters.sif_potential),
                    and_(SafetyReport.final_sif_potential.is_(None), SafetyReport.ai_sif_potential == filters.sif_potential),
                )
            )

        if filters.urgency_level and filters.urgency_level != "ALL":
            if filters.urgency_level == "HIGH" or filters.urgency_level == "CRITICAL":
                conditions.append(SafetyReport.ai_urgency_score >= 85)
            elif filters.urgency_level == "MEDIUM":
                conditions.append(and_(SafetyReport.ai_urgency_score >= 60, SafetyReport.ai_urgency_score < 85))
            elif filters.urgency_level == "LOW":
                conditions.append(SafetyReport.ai_urgency_score < 60)

        if filters.life_saving_rule and filters.life_saving_rule != "ALL":
            conditions.append(
                or_(
                    and_(SafetyReport.final_life_saving_rule.isnot(None), SafetyReport.final_life_saving_rule == filters.life_saving_rule),
                    and_(SafetyReport.final_life_saving_rule.is_(None), SafetyReport.ai_life_saving_rule == filters.life_saving_rule),
                )
            )

        if filters.review_status and filters.review_status != "ALL":
            conditions.append(SafetyReport.review_status == filters.review_status)

        if filters.activity and filters.activity != "ALL":
            conditions.append(SafetyReport.activity.ilike(f"%{filters.activity}%"))

        if conditions:
            query = query.where(and_(*conditions))

        # Count total matches
        count_stmt = select(func.count()).select_from(query.subquery())
        total_count = (await self.db.execute(count_stmt)).scalar_one()

        # Sorting
        sort_col = getattr(SafetyReport, filters.sort_by, SafetyReport.created_at)
        if filters.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_col))
        else:
            query = query.order_by(desc(sort_col))

        # Include relations
        query = query.options(
            joinedload(SafetyReport.facility),
            joinedload(SafetyReport.reporter),
        )

        # Pagination
        query = query.offset(page_params.offset).limit(page_params.limit)

        result = await self.db.execute(query)
        reports = result.scalars().all()
        return reports, total_count

    async def get_review_queue(
        self,
        tab: str = "PENDING",
        page_params: Optional[PageParams] = None,
    ) -> Tuple[Sequence[SafetyReport], int]:
        """Fetch items for human review queue with tab filtering."""
        query = select(SafetyReport).options(
            joinedload(SafetyReport.facility),
            joinedload(SafetyReport.reporter),
        )

        if tab == "PENDING":
            query = query.where(SafetyReport.review_status == ReviewStatus.PENDING.value)
        elif tab == "CRITICAL":
            query = query.where(
                or_(
                    SafetyReport.ai_sif_potential == SIFPotential.CRITICAL.value,
                    SafetyReport.ai_sif_potential == SIFPotential.HIGH.value,
                )
            )
        elif tab == "LOW_CONF":
            query = query.where(SafetyReport.ai_confidence < 94.0)

        # Sort by highest urgency first
        query = query.order_by(desc(SafetyReport.ai_urgency_score), desc(SafetyReport.created_at))

        count_stmt = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_stmt)).scalar_one()

        if page_params:
            query = query.offset(page_params.offset).limit(page_params.limit)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def generate_next_report_id(self) -> str:
        """Generate a sequential SIF report ID: SIF-YYYY-XXXXX."""
        year = datetime.now(timezone.utc).year
        stmt = select(func.count(SafetyReport.id))
        count = (await self.db.execute(stmt)).scalar_one()
        return f"SIF-{year}-{str(count + 1).zfill(5)}"
