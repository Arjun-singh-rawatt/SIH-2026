"""Human-in-the-loop safety triage and validation service (MongoDB backed)."""

from datetime import datetime, timezone
from typing import Tuple, Sequence, Optional
from app.db.repositories.mongo_report_repo import MongoReportRepository
from app.services.report_service import ReportService
from app.schemas.review import ReviewSubmitRequest, ReviewQueueSummary
from app.schemas.report import ReportRead, ReportDetail
from app.utils.pagination import PageParams, PaginatedResponse
from app.utils.enums import ReviewStatus, SIFPotential, SIFPrecursor
from app.core.errors import ReportNotFoundException


class ReviewService:
    def __init__(self, report_repo: MongoReportRepository, report_service: ReportService):
        self.repo = report_repo
        self.report_service = report_service

    async def get_queue(
        self,
        tab: str = "PENDING",
        page_params: Optional[PageParams] = None,
    ) -> PaginatedResponse[ReportRead]:
        reports, total = await self.repo.get_review_queue(tab=tab, page_params=page_params or PageParams(page=1, page_size=20))
        items = [self.report_service._to_read_schema(r) for r in reports]
        return PaginatedResponse.create(items=items, total=total, params=page_params or PageParams(page=1, page_size=20))

    async def get_queue_summary(self) -> ReviewQueueSummary:
        _, pending_count = await self.repo.get_review_queue(tab="PENDING")
        _, critical_count = await self.repo.get_review_queue(tab="CRITICAL")
        _, low_conf_count = await self.repo.get_review_queue(tab="LOW_CONF")
        total_count = await self.repo.count()

        return ReviewQueueSummary(
            pending_count=pending_count,
            critical_count=critical_count,
            low_confidence_count=low_conf_count,
            total_count=total_count,
        )

    async def submit_review(self, identifier: str, request: ReviewSubmitRequest) -> ReportDetail:
        report = await self.repo.get_by_identifier(identifier)
        if not report:
            raise ReportNotFoundException(identifier)

        now = datetime.now(timezone.utc).isoformat()
        updates = {
            "review.reviewer_id": request.reviewer_id or "USR-001",
            "review.reviewer_notes": request.reviewer_notes,
            "review.reviewed_at": now,
            "updated_at": now
        }

        action = request.action.upper()

        if action == "APPROVE":
            updates["review.status"] = ReviewStatus.APPROVED.value
            updates["review.final_sif_potential"] = report.get("analysis", {}).get("sif_potential")
            updates["review.final_sif_precursor"] = report.get("analysis", {}).get("sif_precursor")
            updates["review.final_life_saving_rule"] = report.get("analysis", {}).get("life_saving_rule")
            updates["review.final_failed_barrier"] = report.get("analysis", {}).get("failed_barrier")
            updates["review.final_barrier_status"] = report.get("analysis", {}).get("barrier_status")

        elif action == "MODIFY":
            updates["review.status"] = ReviewStatus.MODIFIED.value
            if request.final_sif_potential:
                updates["review.final_sif_potential"] = request.final_sif_potential
            if request.final_sif_precursor:
                updates["review.final_sif_precursor"] = request.final_sif_precursor
            if request.final_life_saving_rule:
                updates["review.final_life_saving_rule"] = request.final_life_saving_rule
            if request.final_failed_barrier:
                updates["review.final_failed_barrier"] = request.final_failed_barrier
            if request.final_barrier_status:
                updates["review.final_barrier_status"] = request.final_barrier_status

        elif action == "MARK_NON_SIF":
            updates["review.status"] = ReviewStatus.MODIFIED.value
            updates["review.final_sif_potential"] = SIFPotential.NON_SIF.value
            updates["review.final_sif_precursor"] = SIFPrecursor.NO.value

        elif action == "ESCALATE":
            updates["review.status"] = ReviewStatus.ESCALATED.value

        else:
            updates["review.status"] = ReviewStatus.APPROVED.value

        await self.repo.update(report["report_id"], updates)
        return await self.report_service.get_report_by_id(report["report_id"])
