"""SafetyReport lifecycle and ingestion service (MongoDB backed)."""

from typing import Optional, List, Tuple
from datetime import datetime, timezone
from app.db.repositories.mongo_report_repo import MongoReportRepository
from app.db.repositories.facility_repo import FacilityRepository
from app.services.analysis_service import AnalysisService
from app.vector.base import VectorStore, EmbeddingProvider
from app.schemas.report import ReportCreate, ReportUpdate, ReportRead, ReportDetail, ReportStats
from app.schemas.analysis import AnalyzeRequest
from app.schemas.facility import FacilityRead
from app.utils.filters import ReportFilterParams
from app.utils.pagination import PageParams, PaginatedResponse
from app.utils.enums import ReviewStatus, SIFPotential, BarrierStatus
from app.core.errors import ReportNotFoundException, FacilityNotFoundException
from bson import ObjectId

class ReportService:
    def __init__(
        self,
        report_repo: MongoReportRepository,
        facility_repo: FacilityRepository,
        analysis_service: AnalysisService,
        vector_store: VectorStore,
        embedding_provider: EmbeddingProvider,
    ):
        self.repo = report_repo
        self.facility_repo = facility_repo
        self.analysis_service = analysis_service
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider

    def _to_read_schema(self, r: dict) -> ReportRead:
        evidence_phrases = []
        if r.get("analysis", {}).get("evidence_phrase"):
            evidence_phrases = [p.strip() for p in r["analysis"]["evidence_phrase"].split(";") if p.strip()]

        created_at = r.get("created_at") or datetime.now(timezone.utc)
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except ValueError:
                created_at = datetime.now(timezone.utc)
                
        updated_at = r.get("updated_at") or datetime.now(timezone.utc)
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
            except ValueError:
                updated_at = datetime.now(timezone.utc)

        meta = r.get("metadata", {})
        analysis = r.get("analysis", {})
        risk = r.get("risk", {})
        review = r.get("review", {})

        return ReportRead(
            id=str(r.get("_id", "")),
            report_id=r.get("report_id", ""),
            reporter_id=meta.get("reporter_id", ""),
            facility_id=meta.get("facility_id", ""),
            facility_name=meta.get("facility_name", ""),
            region=meta.get("region", ""),
            location=meta.get("location", ""),
            raw_report_text=r.get("raw_report_text", ""),
            language=analysis.get("language", "English"),
            report_type=meta.get("report_type", ""),
            activity=analysis.get("activity", ""),
            primary_hazard=analysis.get("hazard", ""),
            precursor_category=analysis.get("precursor_category", ""),
            potential_consequence=meta.get("potential_consequence", ""),
            ai_sif_potential=analysis.get("sif_potential", ""),
            ai_sif_precursor=analysis.get("sif_precursor", ""),
            ai_confidence=analysis.get("confidence", 0.0),
            ai_urgency_score=risk.get("urgency_score", 0),
            ai_life_saving_rule=analysis.get("life_saving_rule", ""),
            ai_failed_barrier=analysis.get("failed_barrier", ""),
            ai_barrier_status=analysis.get("barrier_status", ""),
            ai_evidence_phrase=analysis.get("evidence_phrase", ""),
            ai_explanation=analysis.get("explanation", ""),
            review_status=review.get("status", "PENDING_REVIEW"),
            reviewer_id=review.get("reviewer_id", ""),
            reviewer_notes=review.get("reviewer_notes", ""),
            reviewed_at=review.get("reviewed_at", None),
            final_sif_potential=review.get("final_sif_potential", None),
            final_sif_precursor=review.get("final_sif_precursor", None),
            final_life_saving_rule=review.get("final_life_saving_rule", None),
            final_failed_barrier=review.get("final_failed_barrier", None),
            final_barrier_status=review.get("final_barrier_status", None),
            sif_potential=review.get("final_sif_potential") or analysis.get("sif_potential", ""),
            sif_precursor=review.get("final_sif_precursor") or analysis.get("sif_precursor", ""),
            confidence=analysis.get("confidence", 0.0),
            urgency_score=risk.get("urgency_score", 0),
            life_saving_rule=review.get("final_life_saving_rule") or analysis.get("life_saving_rule", ""),
            failed_barrier=review.get("final_failed_barrier") or analysis.get("failed_barrier", ""),
            barrier_status=review.get("final_barrier_status") or analysis.get("barrier_status", ""),
            evidence_phrase=analysis.get("evidence_phrase", ""),
            evidence_phrases=evidence_phrases,
            created_at=created_at,
            updated_at=updated_at,
        )

    def _to_detail_schema(self, r: dict) -> ReportDetail:
        base_read = self._to_read_schema(r)
        
        return ReportDetail(
            **base_read.model_dump(),
            facility=None,
            barrier_assessments=[],
            actions=[],
            has_vector_embedding=False,
        )

    async def get_report_by_id(self, identifier: str) -> ReportDetail:
        report = await self.repo.get_by_identifier(identifier)
        if not report:
            raise ReportNotFoundException(identifier)
        return self._to_detail_schema(report)

    async def list_reports(
        self,
        filters: ReportFilterParams,
        page_params: PageParams,
    ) -> PaginatedResponse[ReportRead]:
        reports, total = await self.repo.filter_reports(filters, page_params)
        items = [self._to_read_schema(r) for r in reports]
        return PaginatedResponse.create(items=items, total=total, params=page_params)

    async def create_report(self, payload: ReportCreate) -> ReportDetail:
        if not payload.sif_potential or not payload.life_saving_rule:
            analysis = await self.analysis_service.analyze_report(
                AnalyzeRequest(
                    report_text=payload.raw_report_text,
                    report_type=payload.report_type,
                    facility_id=payload.facility_id,
                    location=payload.location,
                    activity=payload.activity,
                )
            )
            sif_potential = analysis.sif_potential
            sif_precursor = analysis.sif_precursor
            confidence = analysis.confidence
            urgency_score = analysis.urgency_score
            primary_hazard = analysis.primary_hazard
            precursor_category = analysis.precursor_category
            life_saving_rule = analysis.life_saving_rule
            failed_barrier = analysis.failed_barrier
            barrier_status = analysis.barrier_status
            evidence_phrase = analysis.evidence_phrase
            ai_explanation = analysis.ai_explanation
        else:
            sif_potential = payload.sif_potential
            sif_precursor = payload.sif_precursor or "YES"
            confidence = payload.confidence or 94.0
            urgency_score = payload.urgency_score or 85
            primary_hazard = payload.primary_hazard or "Operational Hazard"
            precursor_category = payload.precursor_category or "Operational Safety"
            life_saving_rule = payload.life_saving_rule or "Bypassing Safety Controls"
            failed_barrier = payload.failed_barrier or "Procedural Verification"
            barrier_status = payload.barrier_status or BarrierStatus.FAILED.value
            evidence_phrase = payload.evidence_phrase or ("; ".join(payload.evidence_phrases) if payload.evidence_phrases else "")
            ai_explanation = payload.ai_explanation or "Automated safety intelligence assessment."

        report_id = payload.report_id or await self.repo.generate_next_report_id()

        now = datetime.now(timezone.utc).isoformat()

        document = {
            "report_id": report_id,
            "raw_report_text": payload.raw_report_text,
            "metadata": {
                "reporter_id": payload.reporter_id,
                "reporter_name": payload.reporter_name,
                "facility_id": payload.facility_id,
                "facility_name": payload.facility_name,
                "region": payload.region,
                "location": payload.location,
                "report_type": payload.report_type,
                "potential_consequence": payload.potential_consequence
            },
            "analysis": {
                "language": payload.language,
                "activity": payload.activity,
                "hazard": primary_hazard,
                "sif_precursor": sif_precursor,
                "sif_potential": sif_potential,
                "precursor_category": precursor_category,
                "life_saving_rule": life_saving_rule,
                "failed_barrier": failed_barrier,
                "barrier_status": barrier_status,
                "evidence_phrase": evidence_phrase,
                "explanation": ai_explanation,
                "confidence": confidence
            },
            "risk": {
                "urgency_score": urgency_score,
                "risk_level": "Critical" if urgency_score >= 85 else "High" if urgency_score >= 60 else "Low",
                "escalation_required": urgency_score >= 85
            },
            "review": {
                "status": ReviewStatus.PENDING.value,
                "reviewer_id": None,
                "reviewed_at": None
            },
            "data_status": "Synthetic demo",
            "created_at": now,
            "updated_at": now
        }

        created = await self.repo.create(document)
        return self._to_detail_schema(created)

    async def update_report(self, identifier: str, payload: ReportUpdate) -> ReportDetail:
        report = await self.repo.get_by_identifier(identifier)
        if not report:
            raise ReportNotFoundException(identifier)

        updates = {}
        if payload.review_status:
            updates["review.status"] = payload.review_status
        if payload.final_sif_potential:
            updates["review.final_sif_potential"] = payload.final_sif_potential
            
        if updates:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            await self.repo.update(report["report_id"], updates)

        updated_report = await self.repo.get_by_identifier(identifier)
        return self._to_detail_schema(updated_report)

    async def delete_report(self, identifier: str) -> None:
        report = await self.repo.get_by_identifier(identifier)
        if not report:
            raise ReportNotFoundException(identifier)
        await self.repo.delete(report["report_id"])

    async def get_report_stats(self) -> ReportStats:
        total = await self.repo.count()
        reports, _ = await self.repo.filter_reports(
            ReportFilterParams(),
            PageParams(page=1, page_size=1000),
        )

        sif_count = sum(
            1 for r in reports if r.get("review", {}).get("final_sif_potential", r.get("analysis", {}).get("sif_potential")) in [SIFPotential.CRITICAL.value, SIFPotential.HIGH.value]
        )
        high_urgency = sum(1 for r in reports if r.get("risk", {}).get("urgency_score", 0) >= 85)
        pending_review = sum(1 for r in reports if r.get("review", {}).get("status") == ReviewStatus.PENDING.value)
        sif_density = round((sif_count / total * 100), 2) if total > 0 else 0.0

        return ReportStats(
            total_count=total,
            sif_count=sif_count,
            high_urgency_count=high_urgency,
            pending_review_count=pending_review,
            sif_density=sif_density,
        )
