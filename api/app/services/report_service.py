"""SafetyReport lifecycle and ingestion service."""

from typing import Optional, List, Tuple
from datetime import datetime, timezone
from app.db.repositories.report_repo import ReportRepository
from app.db.repositories.facility_repo import FacilityRepository
from app.db.models.safety_report import SafetyReport
from app.db.models.barrier_assessment import BarrierAssessment
from app.db.models.vector_reference import ReportVectorReference
from app.services.analysis_service import AnalysisService
from app.vector.base import VectorStore, EmbeddingProvider
from app.schemas.report import ReportCreate, ReportUpdate, ReportRead, ReportDetail, ReportStats
from app.schemas.analysis import AnalyzeRequest
from app.schemas.facility import FacilityRead
from app.schemas.barrier import BarrierAssessmentRead
from app.schemas.action import ActionItemRead
from app.schemas.vector import VectorRecord
from app.utils.filters import ReportFilterParams
from app.utils.pagination import PageParams, PaginatedResponse
from app.utils.enums import ReviewStatus, SIFPotential, BarrierStatus
from app.core.errors import ReportNotFoundException, FacilityNotFoundException


class ReportService:
    def __init__(
        self,
        report_repo: ReportRepository,
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

    def _to_read_schema(self, r: SafetyReport) -> ReportRead:
        fac_name = r.facility.name if r.facility else r.facility_id
        reg = r.facility.region if r.facility else "Upper Assam Basin"

        evidence_phrases = []
        if r.ai_evidence_phrase:
            evidence_phrases = [p.strip() for p in r.ai_evidence_phrase.split(";") if p.strip()]

        return ReportRead(
            id=r.id,
            report_id=r.report_id,
            reporter_id=r.reporter_id,
            facility_id=r.facility_id,
            facility_name=fac_name,
            region=reg,
            location=r.location,
            raw_report_text=r.raw_report_text,
            language=r.language,
            report_type=r.report_type,
            activity=r.activity,
            primary_hazard=r.ai_primary_hazard,
            precursor_category=r.ai_precursor_category,
            potential_consequence=r.potential_consequence,
            ai_sif_potential=r.ai_sif_potential,
            ai_sif_precursor=r.ai_sif_precursor,
            ai_confidence=r.ai_confidence,
            ai_urgency_score=r.ai_urgency_score,
            ai_life_saving_rule=r.ai_life_saving_rule,
            ai_failed_barrier=r.ai_failed_barrier,
            ai_barrier_status=r.ai_barrier_status,
            ai_evidence_phrase=r.ai_evidence_phrase,
            ai_explanation=r.ai_explanation,
            review_status=r.review_status,
            reviewer_id=r.reviewer_id,
            reviewer_notes=r.reviewer_notes,
            reviewed_at=r.reviewed_at,
            final_sif_potential=r.final_sif_potential,
            final_sif_precursor=r.final_sif_precursor,
            final_life_saving_rule=r.final_life_saving_rule,
            final_failed_barrier=r.final_failed_barrier,
            final_barrier_status=r.final_barrier_status,
            sif_potential=r.effective_sif_potential,
            sif_precursor=r.effective_sif_precursor,
            confidence=r.ai_confidence,
            urgency_score=r.ai_urgency_score,
            life_saving_rule=r.effective_life_saving_rule,
            failed_barrier=r.effective_failed_barrier,
            barrier_status=r.effective_barrier_status,
            evidence_phrase=r.ai_evidence_phrase,
            evidence_phrases=evidence_phrases,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )

    def _to_detail_schema(self, r: SafetyReport) -> ReportDetail:
        base_read = self._to_read_schema(r)
        
        fac_schema = None
        if r.facility:
            fac_schema = FacilityRead.model_validate(r.facility)

        barriers = [
            BarrierAssessmentRead(
                id=b.id,
                report_id=b.report_id,
                failed_barrier=b.failed_barrier,
                barrier_status=b.barrier_status,
                barrier_type=b.barrier_type,
                life_saving_rule=b.life_saving_rule,
                description=b.description,
                created_at=b.created_at,
                updated_at=b.updated_at,
            )
            for b in (r.barrier_assessments or [])
        ]

        actions = [
            ActionItemRead(
                id=a.id,
                action_id=a.action_id,
                report_id=a.report_id,
                report_title=r.ai_primary_hazard,
                assigned_to=a.assigned_to,
                assignee_name=a.assignee.name if a.assignee else a.assigned_to,
                assignee_role=a.assignee.role if a.assignee else None,
                facility_id=a.facility_id,
                facility_name=a.facility.short_name if a.facility else a.facility_id,
                action_type=a.action_type,
                description=a.description,
                priority=a.priority,
                status=a.status,
                due_date=a.due_date,
                completed_at=a.completed_at,
                created_at=a.created_at,
                updated_at=a.updated_at,
            )
            for a in (r.actions or [])
        ]

        return ReportDetail(
            **base_read.model_dump(),
            facility=fac_schema,
            barrier_assessments=barriers,
            actions=actions,
            has_vector_embedding=r.vector_reference is not None,
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
        # Verify facility exists
        fac = await self.facility_repo.get_by_facility_id(payload.facility_id)
        if not fac:
            # Fallback to first facility if unknown
            facilities = await self.facility_repo.get_all_active()
            fac = facilities[0] if facilities else None

        # 1. Run AI analysis if not fully provided
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
            potential_consequence = payload.potential_consequence or analysis.potential_consequence
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
            potential_consequence = payload.potential_consequence

        # 2. Generate sequential report ID
        report_id = payload.report_id or await self.repo.generate_next_report_id()

        # 3. Create SafetyReport model
        report = SafetyReport(
            report_id=report_id,
            reporter_id=payload.reporter_id,
            facility_id=fac.facility_id if fac else payload.facility_id,
            location=payload.location,
            raw_report_text=payload.raw_report_text,
            language=payload.language,
            report_type=payload.report_type,
            activity=payload.activity,
            potential_consequence=potential_consequence,
            # AI predictions
            ai_sif_potential=sif_potential,
            ai_sif_precursor=sif_precursor,
            ai_confidence=confidence,
            ai_urgency_score=urgency_score,
            ai_primary_hazard=primary_hazard,
            ai_precursor_category=precursor_category,
            ai_life_saving_rule=life_saving_rule,
            ai_failed_barrier=failed_barrier,
            ai_barrier_status=barrier_status,
            ai_evidence_phrase=evidence_phrase,
            ai_explanation=ai_explanation,
            # Human review status
            review_status=ReviewStatus.PENDING.value,
        )

        created_report = await self.repo.create(report)

        # 4. Create primary BarrierAssessment
        if failed_barrier:
            barrier = BarrierAssessment(
                report_id=created_report.report_id,
                failed_barrier=failed_barrier,
                barrier_status=barrier_status,
                life_saving_rule=life_saving_rule,
                description=f"Primary barrier failure diagnosed by AI: {failed_barrier}",
            )
            self.repo.db.add(barrier)
            await self.repo.db.commit()

        # 5. Embed into Vector store
        try:
            vector = await self.embedding_provider.embed_text(created_report.raw_report_text)
            vector_rec = VectorRecord(
                id=created_report.report_id,
                values=vector,
                metadata={
                    "report_id": created_report.report_id,
                    "facility_id": created_report.facility_id,
                    "precursor_category": created_report.ai_precursor_category,
                    "life_saving_rule": created_report.ai_life_saving_rule,
                    "sif_potential": created_report.ai_sif_potential,
                    "primary_hazard": created_report.ai_primary_hazard,
                },
            )
            await self.vector_store.upsert(vector_rec)

            ref = ReportVectorReference(
                report_id=created_report.report_id,
                vector_id=created_report.report_id,
                embedding_model="sift-dense-embed-v1",
                dimension=len(vector),
            )
            self.repo.db.add(ref)
            await self.repo.db.commit()
        except Exception as e:
            # Non-blocking vector store indexing
            pass

        return await self.get_report_by_id(created_report.report_id)

    async def update_report(self, identifier: str, payload: ReportUpdate) -> ReportDetail:
        report = await self.repo.get_by_identifier(identifier)
        if not report:
            raise ReportNotFoundException(identifier)

        update_dict = payload.model_dump(exclude_unset=True)
        for key, val in update_dict.items():
            setattr(report, key, val)

        await self.repo.update(report)
        return await self.get_report_by_id(report.report_id)

    async def delete_report(self, identifier: str) -> None:
        report = await self.repo.get_by_identifier(identifier)
        if not report:
            raise ReportNotFoundException(identifier)

        # Delete vector reference if present
        try:
            await self.vector_store.delete(report.report_id)
        except Exception:
            pass

        await self.repo.delete(report)

    async def get_report_stats(self) -> ReportStats:
        total = await self.repo.count()
        reports, _ = await self.repo.filter_reports(
            ReportFilterParams(),
            PageParams(page=1, page_size=1000),
        )

        sif_count = sum(
            1 for r in reports if r.effective_sif_potential in [SIFPotential.CRITICAL.value, SIFPotential.HIGH.value]
        )
        high_urgency = sum(1 for r in reports if r.ai_urgency_score >= 85)
        pending_review = sum(1 for r in reports if r.review_status == ReviewStatus.PENDING.value)
        sif_density = round((sif_count / total * 100), 2) if total > 0 else 0.0

        return ReportStats(
            total_count=total,
            sif_count=sif_count,
            high_urgency_count=high_urgency,
            pending_review_count=pending_review,
            sif_density=sif_density,
        )
