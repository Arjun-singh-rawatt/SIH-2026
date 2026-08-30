"""Facility repository and aggregation calculations."""

from typing import Optional, Sequence, Dict, Any, List
from sqlalchemy import select, func, or_, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.facility import Facility
from app.db.models.safety_report import SafetyReport
from app.db.models.action_item import ActionItem
from app.db.repositories.base_repo import BaseRepository
from app.utils.enums import ActionStatus, SIFPotential


class FacilityRepository(BaseRepository[Facility]):
    def __init__(self, db: AsyncSession):
        super().__init__(Facility, db)

    async def get_by_facility_id(self, facility_id: str) -> Optional[Facility]:
        stmt = select(Facility).where(
            or_(
                Facility.facility_id == facility_id,
                Facility.id == facility_id,
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_all_active(self) -> Sequence[Facility]:
        stmt = select(Facility).where(Facility.active.is_(True)).order_by(Facility.facility_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_facility_stats(self, facility_id: str) -> Dict[str, Any]:
        """Compute aggregated safety metrics for a specific facility."""
        fac = await self.get_by_facility_id(facility_id)
        if not fac:
            return {}

        # 1. Total reports
        total_stmt = select(func.count(SafetyReport.id)).where(SafetyReport.facility_id == fac.facility_id)
        total_reports = (await self.db.execute(total_stmt)).scalar_one()

        # 2. SIF reports (High or Critical SIF)
        sif_stmt = select(func.count(SafetyReport.id)).where(
            and_(
                SafetyReport.facility_id == fac.facility_id,
                or_(
                    SafetyReport.final_sif_potential.in_([SIFPotential.CRITICAL.value, SIFPotential.HIGH.value]),
                    and_(
                        SafetyReport.final_sif_potential.is_(None),
                        SafetyReport.ai_sif_potential.in_([SIFPotential.CRITICAL.value, SIFPotential.HIGH.value]),
                    ),
                ),
            )
        )
        sif_reports = (await self.db.execute(sif_stmt)).scalar_one()
        sif_density = round((sif_reports / total_reports * 100), 2) if total_reports > 0 else 0.0

        # 3. High urgency count (urgency >= 85)
        urgency_stmt = select(func.count(SafetyReport.id)).where(
            and_(
                SafetyReport.facility_id == fac.facility_id,
                SafetyReport.ai_urgency_score >= 85,
            )
        )
        high_urgency_count = (await self.db.execute(urgency_stmt)).scalar_one()

        # 4. Open action items
        actions_stmt = select(func.count(ActionItem.id)).where(
            and_(
                ActionItem.facility_id == fac.facility_id,
                ActionItem.status.in_([ActionStatus.OPEN.value, ActionStatus.IN_PROGRESS.value, ActionStatus.OVERDUE.value]),
            )
        )
        open_actions = (await self.db.execute(actions_stmt)).scalar_one()

        # 5. Top precursor
        precursor_stmt = (
            select(SafetyReport.ai_precursor_category, func.count(SafetyReport.id).label("cnt"))
            .where(SafetyReport.facility_id == fac.facility_id)
            .group_by(SafetyReport.ai_precursor_category)
            .order_by(desc("cnt"))
            .limit(1)
        )
        top_precursor_row = (await self.db.execute(precursor_stmt)).first()
        top_precursor = top_precursor_row[0] if top_precursor_row else "Energy Isolation"

        # 6. Top activity
        activity_stmt = (
            select(SafetyReport.activity, func.count(SafetyReport.id).label("cnt"))
            .where(SafetyReport.facility_id == fac.facility_id)
            .group_by(SafetyReport.activity)
            .order_by(desc("cnt"))
            .limit(1)
        )
        top_activity_row = (await self.db.execute(activity_stmt)).first()
        top_activity = top_activity_row[0] if top_activity_row else "Plant Maintenance"

        # 7. Primary hazard
        hazard_stmt = (
            select(SafetyReport.ai_primary_hazard, func.count(SafetyReport.id).label("cnt"))
            .where(SafetyReport.facility_id == fac.facility_id)
            .group_by(SafetyReport.ai_primary_hazard)
            .order_by(desc("cnt"))
            .limit(1)
        )
        top_hazard_row = (await self.db.execute(hazard_stmt)).first()
        primary_hazard = top_hazard_row[0] if top_hazard_row else "Stored Hydrocarbon Energy"

        # Risk level determination
        risk_level = "LOW"
        if sif_density > 24.0 or high_urgency_count > 40:
            risk_level = "CRITICAL"
        elif sif_density > 18.0 or high_urgency_count > 20:
            risk_level = "HIGH"
        elif sif_density > 10.0:
            risk_level = "MEDIUM"

        return {
            "facility_id": fac.facility_id,
            "facility_name": fac.name,
            "short_name": fac.short_name,
            "region": fac.region,
            "type": fac.type,
            "active_personnel": fac.active_personnel,
            "risk_level": risk_level,
            "total_reports": total_reports,
            "sif_reports": sif_reports,
            "sif_density": sif_density,
            "high_urgency_count": high_urgency_count,
            "open_actions": open_actions,
            "top_precursor": top_precursor,
            "top_activity": top_activity,
            "primary_hazard": primary_hazard,
            "manager": fac.manager,
        }
