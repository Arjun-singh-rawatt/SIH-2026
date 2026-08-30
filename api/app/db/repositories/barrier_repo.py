"""BarrierAssessment repository."""

from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.barrier_assessment import BarrierAssessment
from app.db.repositories.base_repo import BaseRepository


class BarrierRepository(BaseRepository[BarrierAssessment]):
    def __init__(self, db: AsyncSession):
        super().__init__(BarrierAssessment, db)

    async def get_by_report_id(self, report_id: str) -> Sequence[BarrierAssessment]:
        stmt = select(BarrierAssessment).where(BarrierAssessment.report_id == report_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
