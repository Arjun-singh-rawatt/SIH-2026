"""MongoDB repository for Safety Reports."""
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Any, Dict
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.utils.filters import ReportFilterParams
from app.utils.pagination import PageParams
from app.utils.enums import ReviewStatus, SIFPotential

class MongoReportRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.reports

    async def get_by_identifier(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Find report by report_id (e.g. OIL-2026-013)."""
        doc = await self.collection.find_one({"report_id": identifier})
        return doc

    async def filter_reports(
        self,
        filters: ReportFilterParams,
        page_params: PageParams,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Execute parameterized filter query with total count and pagination."""
        query = {}

        # Free-text Search
        if filters.search and filters.search.strip():
            q = filters.search.strip()
            query["$or"] = [
                {"report_id": {"$regex": q, "$options": "i"}},
                {"raw_report_text": {"$regex": q, "$options": "i"}},
                {"analysis.primary_hazard": {"$regex": q, "$options": "i"}},
                {"analysis.activity": {"$regex": q, "$options": "i"}},
                {"analysis.life_saving_rule": {"$regex": q, "$options": "i"}},
                {"metadata.location": {"$regex": q, "$options": "i"}},
                {"metadata.facility_name": {"$regex": q, "$options": "i"}}
            ]

        if filters.facility_id and filters.facility_id != "ALL":
            query["metadata.facility_id"] = filters.facility_id

        if filters.report_type and filters.report_type != "ALL":
            query["metadata.report_type"] = filters.report_type

        if filters.sif_potential and filters.sif_potential != "ALL":
            query["analysis.sif_potential"] = filters.sif_potential

        if filters.urgency_level and filters.urgency_level != "ALL":
            if filters.urgency_level in ["HIGH", "CRITICAL"]:
                query["risk.urgency_score"] = {"$gte": 85}
            elif filters.urgency_level == "MEDIUM":
                query["risk.urgency_score"] = {"$gte": 60, "$lt": 85}
            elif filters.urgency_level == "LOW":
                query["risk.urgency_score"] = {"$lt": 60}

        if filters.life_saving_rule and filters.life_saving_rule != "ALL":
            query["analysis.life_saving_rule"] = filters.life_saving_rule

        if filters.review_status and filters.review_status != "ALL":
            query["review.status"] = filters.review_status

        if filters.activity and filters.activity != "ALL":
            query["analysis.activity"] = {"$regex": filters.activity, "$options": "i"}

        total_count = await self.collection.count_documents(query)

        sort_field = filters.sort_by if filters.sort_by else "created_at"
        # map generic sort fields to mongo document fields
        if sort_field == "created_at":
            sort_field = "created_at"
        elif sort_field == "urgency_score" or sort_field == "ai_urgency_score":
            sort_field = "risk.urgency_score"
            
        sort_dir = 1 if filters.sort_order.lower() == "asc" else -1

        cursor = self.collection.find(query).sort([(sort_field, sort_dir)]).skip(page_params.offset).limit(page_params.limit)
        reports = await cursor.to_list(length=page_params.limit)
        
        return reports, total_count

    async def get_review_queue(
        self,
        tab: str = "PENDING",
        page_params: Optional[PageParams] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = {}
        if tab == "PENDING":
            query["review.status"] = ReviewStatus.PENDING.value
        elif tab == "CRITICAL":
            query["analysis.sif_potential"] = {"$in": [SIFPotential.CRITICAL.value, SIFPotential.HIGH.value]}
        elif tab == "LOW_CONF":
            query["analysis.confidence"] = {"$lt": 94.0}

        total = await self.collection.count_documents(query)
        
        cursor = self.collection.find(query).sort([("risk.urgency_score", -1), ("created_at", -1)])
        if page_params:
            cursor = cursor.skip(page_params.offset).limit(page_params.limit)
            
        reports = await cursor.to_list(length=page_params.limit if page_params else 100)
        return reports, total

    async def generate_next_report_id(self) -> str:
        """Generate a sequential SIF report ID: OIL-YYYY-XXXXX."""
        year = datetime.now(timezone.utc).year
        count = await self.collection.count_documents({})
        return f"OIL-{year}-{str(count + 1).zfill(5)}"

    async def create(self, document: dict) -> dict:
        result = await self.collection.insert_one(document)
        document["_id"] = result.inserted_id
        return document

    async def update(self, report_id: str, updates: dict) -> None:
        await self.collection.update_one(
            {"report_id": report_id},
            {"$set": updates}
        )

    async def delete(self, report_id: str) -> None:
        await self.collection.delete_one({"report_id": report_id})

    async def count(self) -> int:
        return await self.collection.count_documents({})
