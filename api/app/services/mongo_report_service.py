"""MongoDB source-of-truth implementation for report creation, retrieval and listing."""

from datetime import datetime, timezone
from app.core.errors import ReportNotFoundException, SIFTException
from app.db.mongodb import get_mongo_db
from app.schemas.analysis import AnalyzeRequest
from app.schemas.report import ReportCreate, ReportDetail, ReportRead, ReportStats, ReportUpdate
from app.services.analysis_service import AnalysisService
from app.utils.filters import ReportFilterParams
from app.utils.pagination import PageParams, PaginatedResponse


class MongoReportService:
    def __init__(self, analysis_service: AnalysisService):
        self.analysis_service = analysis_service

    @staticmethod
    def _read(document: dict) -> ReportRead:
        meta, analysis, risk, review = (document.get("metadata", {}), document.get("analysis", {}),
                                        document.get("risk", {}), document.get("review", {}))
        evidence = analysis.get("evidence", [])
        return ReportRead(
            id=str(document["_id"]), report_id=document["report_id"], reporter_id=meta.get("reporter_id", "USR-002"),
            facility_id=meta.get("facility_id", "FAC-DEMO-01"), facility_name=meta.get("facility_name"),
            region=meta.get("region", "Demo Operations"), location=meta.get("location", "Field Location"),
            raw_report_text=document["raw_report_text"], language=analysis.get("language", meta.get("language", "English")),
            report_type=meta.get("report_type", "Unsafe Condition"), activity=analysis.get("activity", meta.get("activity", "Field Safety Observation")),
            primary_hazard=analysis.get("hazard", "Assessment pending"), precursor_category=analysis.get("precursor_category", "Assessment pending"),
            potential_consequence=analysis.get("potential_consequence"), ai_sif_potential=analysis.get("sif_potential", "PENDING"),
            ai_sif_precursor=analysis.get("sif_precursor", "POTENTIAL"), ai_confidence=analysis.get("confidence", 0.0),
            ai_urgency_score=risk.get("urgency_score", 0), ai_life_saving_rule=analysis.get("life_saving_rule", "Assessment pending"),
            ai_failed_barrier=analysis.get("failed_barrier"), ai_barrier_status=analysis.get("barrier_status", "UNKNOWN"),
            ai_evidence_phrase="; ".join(evidence), ai_explanation=analysis.get("explanation"),
            review_status=review.get("status", "AI_PENDING"), reviewer_id=review.get("reviewer_id"), reviewer_notes=review.get("reviewer_notes"),
            reviewed_at=review.get("reviewed_at"), final_sif_potential=review.get("final_sif_potential"),
            final_sif_precursor=review.get("final_sif_precursor"), final_life_saving_rule=review.get("final_life_saving_rule"),
            final_failed_barrier=review.get("final_failed_barrier"), final_barrier_status=review.get("final_barrier_status"),
            sif_potential=review.get("final_sif_potential") or analysis.get("sif_potential", "PENDING"),
            sif_precursor=review.get("final_sif_precursor") or analysis.get("sif_precursor", "POTENTIAL"),
            confidence=analysis.get("confidence", 0.0), urgency_score=risk.get("urgency_score", 0),
            life_saving_rule=review.get("final_life_saving_rule") or analysis.get("life_saving_rule", "Assessment pending"),
            failed_barrier=review.get("final_failed_barrier") or analysis.get("failed_barrier") or "Assessment pending",
            barrier_status=review.get("final_barrier_status") or analysis.get("barrier_status", "UNKNOWN"),
            evidence_phrase="; ".join(evidence), evidence_phrases=evidence, created_at=document["created_at"], updated_at=document["updated_at"],
        )

    async def create_report(self, payload: ReportCreate) -> ReportDetail:
        from pymongo import ReturnDocument
        from pymongo.errors import DuplicateKeyError
        db, now = get_mongo_db(), datetime.now(timezone.utc)
        sequence = db.counters.find_one_and_update(
            {"_id": "report_sequence"}, {"$inc": {"value": 1}}, upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        number = sequence.get("value", 1)
        report_id = payload.report_id or f"OIL-{now.year}-{number:04d}"
        document = {"report_id": report_id, "raw_report_text": payload.raw_report_text,
            "metadata": {"reporter_id": payload.reporter_id, "reporter_name": payload.reporter_name, "facility_id": payload.facility_id,
                "facility_name": payload.facility_name or payload.facility_id, "region": payload.region or "Demo Operations", "location": payload.location,
                "report_type": payload.report_type, "activity": payload.activity, "language": payload.language},
            "analysis": {}, "risk": {}, "review": {"status": "AI_PENDING", "reviewer_id": None, "reviewed_at": None},
            "data_status": "Synthetic demo", "created_at": now, "updated_at": now}
        try:
            inserted = db.reports.insert_one(document)
        except DuplicateKeyError:
            raise SIFTException(409, "DUPLICATE_REPORT_ID", f"Report ID '{report_id}' already exists.")
        try:
            result = await self.analysis_service.analyze_report(AnalyzeRequest(report_text=payload.raw_report_text, report_type=payload.report_type, facility_id=payload.facility_id, location=payload.location, activity=payload.activity))
            analysis = {"language": payload.language, "activity": result.activity, "hazard": result.primary_hazard, "sif_precursor": result.sif_precursor,
                "sif_potential": result.sif_potential, "precursor_category": result.precursor_category, "evidence": result.evidence_phrases,
                "failed_barrier": result.failed_barrier, "barrier_status": result.barrier_status, "life_saving_rule": result.life_saving_rule,
                "confidence": result.confidence, "potential_consequence": result.potential_consequence, "explanation": result.ai_explanation}
            risk = {"urgency_score": result.urgency_score, "risk_level": result.sif_potential, "escalation_required": result.sif_potential in {"CRITICAL", "HIGH"}}
            db.reports.update_one({"_id": inserted.inserted_id}, {"$set": {"analysis": analysis, "risk": risk, "review.status": "PENDING_REVIEW", "updated_at": datetime.now(timezone.utc)}})
        except Exception:
            # The raw report remains safely persisted and explicitly pending analysis.
            pass
        return await self.get_report_by_id(report_id)

    async def get_report_by_id(self, identifier: str) -> ReportDetail:
        document = get_mongo_db().reports.find_one({"report_id": identifier})
        if not document:
            raise ReportNotFoundException(identifier)
        return ReportDetail(**self._read(document).model_dump(), facility=None, barrier_assessments=[], actions=[], has_vector_embedding=False)

    async def list_reports(self, filters: ReportFilterParams, page_params: PageParams) -> PaginatedResponse[ReportRead]:
        query = {}
        if filters.facility_id and filters.facility_id != "ALL": query["metadata.facility_id"] = filters.facility_id
        if filters.report_type and filters.report_type != "ALL": query["metadata.report_type"] = filters.report_type
        if filters.sif_potential and filters.sif_potential != "ALL": query["analysis.sif_potential"] = filters.sif_potential.upper()
        if filters.review_status and filters.review_status != "ALL": query["review.status"] = filters.review_status
        if filters.search:
            escaped = {"$regex": filters.search, "$options": "i"}
            query["$or"] = [{"report_id": escaped}, {"raw_report_text": escaped}, {"metadata.location": escaped}, {"analysis.hazard": escaped}, {"analysis.precursor_category": escaped}]
        allowed = {"created_at", "updated_at", "urgency_score", "confidence"}
        field = {"urgency_score": "risk.urgency_score", "confidence": "analysis.confidence"}.get(filters.sort_by, filters.sort_by)
        if filters.sort_by not in allowed: field = "created_at"
        direction = 1 if filters.sort_order.lower() == "asc" else -1
        collection = get_mongo_db().reports
        total = collection.count_documents(query)
        docs = list(collection.find(query).sort(field, direction).skip(page_params.offset).limit(page_params.limit))
        return PaginatedResponse.create([self._read(d) for d in docs], total, page_params)

    async def update_report(self, identifier: str, payload: ReportUpdate) -> ReportDetail:
        updates = payload.model_dump(exclude_unset=True)
        if updates: get_mongo_db().reports.update_one({"report_id": identifier}, {"$set": {**{f"review.{k}": v for k, v in updates.items()}, "updated_at": datetime.now(timezone.utc)}})
        return await self.get_report_by_id(identifier)

    async def get_report_stats(self) -> ReportStats:
        docs = list(get_mongo_db().reports.find({}, {"analysis": 1, "risk": 1, "review": 1}))
        total = len(docs); sif = sum(d.get("analysis", {}).get("sif_potential") in {"HIGH", "CRITICAL"} for d in docs)
        return ReportStats(total_count=total, sif_count=sif, high_urgency_count=sum(d.get("risk", {}).get("urgency_score", 0) >= 85 for d in docs), pending_review_count=sum(d.get("review", {}).get("status") == "PENDING_REVIEW" for d in docs), sif_density=round(sif * 100 / total, 2) if total else 0)
