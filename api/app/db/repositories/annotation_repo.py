"""SIFT Annotation Workbench Database Repository.

Provides transactional query access to batches, tasks, assignments, submissions,
disagreement isolation, and expert adjudication records.
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple
from datetime import datetime, timezone
import uuid
from sqlalchemy import select, func, or_, and_, desc, asc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.annotation import (
    AnnotationBatch,
    AnnotationTask,
    AnnotationAssignment,
    AnnotationSubmissionRecord,
    DisagreementRecord,
    AdjudicationRecord,
)
from app.db.models.safety_report import SafetyReport
from app.db.models.user import User


class AnnotationRepository:
    """Transactional database repository for human annotation workflows."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_batches(self) -> Sequence[AnnotationBatch]:
        """List all registered annotation batches ordered by creation timestamp."""
        stmt = (
            select(AnnotationBatch)
            .options(
                selectinload(AnnotationBatch.tasks).selectinload(AnnotationTask.assignments),
                joinedload(AnnotationBatch.creator),
            )
            .order_by(AnnotationBatch.created_at.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def get_batch_by_id(self, batch_id_or_uuid: str) -> Optional[AnnotationBatch]:
        """Find batch by UUID or business batch_id (e.g. BATCH-2026-001)."""
        stmt = (
            select(AnnotationBatch)
            .options(
                selectinload(AnnotationBatch.tasks).selectinload(AnnotationTask.assignments),
                joinedload(AnnotationBatch.creator),
            )
            .where(
                or_(
                    AnnotationBatch.id == batch_id_or_uuid,
                    AnnotationBatch.batch_id == batch_id_or_uuid,
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def create_batch(
        self,
        batch_id: str,
        name: str,
        source_id: str,
        report_ids: List[str],
        annotator_a_id: str,
        annotator_b_id: str,
        created_by_id: str,
        is_demo: bool = True,
        notes: Optional[str] = None,
    ) -> AnnotationBatch:
        """Create a new batch, instantiate tasks, and dual-assign Annotator A & B."""
        batch = AnnotationBatch(
            id=str(uuid.uuid4()),
            batch_id=batch_id,
            name=name,
            source_id=source_id,
            status="IN_PROGRESS",
            record_count=len(report_ids),
            is_demo=is_demo,
            notes=notes,
            created_by_id=created_by_id,
        )
        self.db.add(batch)
        await self.db.flush()

        for idx, r_id in enumerate(report_ids):
            task = AnnotationTask(
                id=str(uuid.uuid4()),
                batch_id=batch.id,
                report_id=r_id,
                status="PENDING",
                order_index=idx,
            )
            self.db.add(task)
            await self.db.flush()

            # Assign Annotator A
            assign_a = AnnotationAssignment(
                id=str(uuid.uuid4()),
                task_id=task.id,
                annotator_id=annotator_a_id,
                role_slot="ANNOTATOR_A",
                status="ASSIGNED",
            )
            # Assign Annotator B
            assign_b = AnnotationAssignment(
                id=str(uuid.uuid4()),
                task_id=task.id,
                annotator_id=annotator_b_id,
                role_slot="ANNOTATOR_B",
                status="ASSIGNED",
            )
            self.db.add(assign_a)
            self.db.add(assign_b)

        await self.db.commit()
        return await self.get_batch_by_id(batch.id)

    async def get_tasks(
        self,
        batch_id: Optional[str] = None,
        annotator_id: Optional[str] = None,
    ) -> Sequence[AnnotationTask]:
        """Query tasks with optional batch and annotator filters."""
        stmt = (
            select(AnnotationTask)
            .options(
                joinedload(AnnotationTask.batch),
                joinedload(AnnotationTask.report),
                selectinload(AnnotationTask.assignments).joinedload(AnnotationAssignment.submission),
            )
            .order_by(AnnotationTask.order_index.asc())
        )
        if batch_id:
            stmt = stmt.where(
                or_(
                    AnnotationTask.batch_id == batch_id,
                    AnnotationTask.batch.has(AnnotationBatch.batch_id == batch_id),
                )
            )
        if annotator_id:
            stmt = stmt.where(
                AnnotationTask.assignments.any(AnnotationAssignment.annotator_id == annotator_id)
            )

        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def get_task_by_id(self, task_id: str) -> Optional[AnnotationTask]:
        """Fetch full task details with report and assignments."""
        stmt = (
            select(AnnotationTask)
            .options(
                joinedload(AnnotationTask.batch),
                joinedload(AnnotationTask.report).joinedload(SafetyReport.facility),
                selectinload(AnnotationTask.assignments).joinedload(AnnotationAssignment.submission),
                selectinload(AnnotationTask.disagreements),
                joinedload(AnnotationTask.adjudication),
            )
            .where(
                or_(
                    AnnotationTask.id == task_id,
                    AnnotationTask.report_id == task_id,
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def get_assignment(self, task_id: str, annotator_id: str) -> Optional[AnnotationAssignment]:
        """Fetch assignment slot for specific task and annotator."""
        stmt = (
            select(AnnotationAssignment)
            .options(
                joinedload(AnnotationAssignment.submission),
                joinedload(AnnotationAssignment.task),
            )
            .where(
                and_(
                    AnnotationAssignment.task_id == task_id,
                    AnnotationAssignment.annotator_id == annotator_id,
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def save_or_update_submission(
        self,
        assignment: AnnotationAssignment,
        payload_dict: Dict[str, Any],
        is_draft: bool,
    ) -> AnnotationSubmissionRecord:
        """Create or update an annotation submission record."""
        sub = assignment.submission
        now = datetime.now(timezone.utc)

        if sub is None:
            sub = AnnotationSubmissionRecord(
                id=str(uuid.uuid4()),
                assignment_id=assignment.id,
                task_id=assignment.task_id,
                annotator_id=assignment.annotator_id,
                is_draft=is_draft,
                submitted_at=None if is_draft else now,
            )
            self.db.add(sub)
        else:
            sub.is_draft = is_draft
            if not is_draft:
                sub.submitted_at = now

        # Map fields
        for field in [
            "sif_potential", "sif_precursor", "primary_hazard", "secondary_hazards",
            "activity", "primary_precursor", "precursor_categories",
            "life_saving_rule", "life_saving_rules", "barriers", "evidence_spans",
            "urgency_score", "potential_consequence", "notes"
        ]:
            if field in payload_dict:
                setattr(sub, field, payload_dict[field])

        # Update assignment state
        assignment.status = "DRAFT" if is_draft else "SUBMITTED"
        await self.db.commit()
        await self.db.refresh(sub)
        return sub

    async def get_task_submissions(self, task_id: str) -> List[AnnotationSubmissionRecord]:
        """Retrieve both submissions for a task."""
        stmt = (
            select(AnnotationSubmissionRecord)
            .options(joinedload(AnnotationSubmissionRecord.annotator))
            .where(AnnotationSubmissionRecord.task_id == task_id)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def record_disagreements(
        self,
        task_id: str,
        disagreements: List[Dict[str, Any]],
    ):
        """Persist field discrepancies for a task and set task state to DISAGREEMENT."""
        # Clear existing pending disagreements for task
        del_stmt = (
            select(DisagreementRecord)
            .where(DisagreementRecord.task_id == task_id)
        )
        del_res = await self.db.execute(del_stmt)
        for existing in del_res.scalars().all():
            await self.db.delete(existing)

        for d in disagreements:
            dis_obj = DisagreementRecord(
                id=str(uuid.uuid4()),
                task_id=task_id,
                field_name=d["field_name"],
                annotator_a_id=d["annotator_a_id"],
                annotator_b_id=d["annotator_b_id"],
                annotator_a_value=d.get("annotator_a_value"),
                annotator_b_value=d.get("annotator_b_value"),
                status="PENDING_ADJUDICATION",
            )
            self.db.add(dis_obj)

        task = await self.get_task_by_id(task_id)
        if task:
            task.status = "DISAGREEMENT" if disagreements else "COMPLETED"

        await self.db.commit()

    async def get_disagreements(self, batch_id: Optional[str] = None) -> Sequence[DisagreementRecord]:
        """List unresolved field disagreements."""
        stmt = (
            select(DisagreementRecord)
            .options(
                joinedload(DisagreementRecord.task).joinedload(AnnotationTask.report),
                joinedload(DisagreementRecord.task).joinedload(AnnotationTask.batch),
            )
            .where(DisagreementRecord.status == "PENDING_ADJUDICATION")
            .order_by(DisagreementRecord.created_at.desc())
        )
        if batch_id:
            stmt = stmt.where(
                DisagreementRecord.task.has(AnnotationTask.batch_id == batch_id)
            )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def get_disagreement_tasks(self, batch_id: Optional[str] = None) -> Sequence[AnnotationTask]:
        """List distinct tasks requiring expert adjudication."""
        stmt = (
            select(AnnotationTask)
            .options(
                joinedload(AnnotationTask.batch),
                joinedload(AnnotationTask.report).joinedload(SafetyReport.facility),
                selectinload(AnnotationTask.disagreements),
                selectinload(AnnotationTask.assignments).joinedload(AnnotationAssignment.submission),
            )
            .where(AnnotationTask.status == "DISAGREEMENT")
            .order_by(AnnotationTask.created_at.desc())
        )
        if batch_id:
            stmt = stmt.where(
                or_(
                    AnnotationTask.batch_id == batch_id,
                    AnnotationTask.batch.has(AnnotationBatch.batch_id == batch_id),
                )
            )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create_adjudication(
        self,
        task_id: str,
        adjudicator_id: str,
        resolution_dict: Dict[str, Any],
    ) -> AdjudicationRecord:
        """Apply Lead HSE Expert adjudication, resolving all discrepancies."""
        task = await self.get_task_by_id(task_id)
        if not task:
            raise FileNotFoundError(f"Task not found: {task_id}")

        adj = task.adjudication
        now = datetime.now(timezone.utc)
        if adj is None:
            adj = AdjudicationRecord(
                id=str(uuid.uuid4()),
                task_id=task_id,
                adjudicator_id=adjudicator_id,
                resolved_sif_potential=str(resolution_dict["resolved_sif_potential"]),
                resolved_sif_precursor=str(resolution_dict["resolved_sif_precursor"]),
                resolved_primary_hazard=resolution_dict["resolved_primary_hazard"],
                resolved_secondary_hazards=resolution_dict.get("resolved_secondary_hazards"),
                resolved_activity=resolution_dict["resolved_activity"],
                resolved_primary_precursor=resolution_dict["resolved_primary_precursor"],
                resolved_precursor_categories=resolution_dict.get("resolved_precursor_categories"),
                resolved_life_saving_rule=resolution_dict["resolved_life_saving_rule"],
                resolved_life_saving_rules=resolution_dict.get("resolved_life_saving_rules"),
                resolved_barriers=resolution_dict.get("resolved_barriers"),
                resolved_evidence_spans=resolution_dict.get("resolved_evidence_spans"),
                adjudication_notes=resolution_dict["adjudication_notes"],
                adjudicated_at=now,
            )
            self.db.add(adj)
        else:
            adj.adjudicator_id = adjudicator_id
            adj.resolved_sif_potential = str(resolution_dict["resolved_sif_potential"])
            adj.resolved_sif_precursor = str(resolution_dict["resolved_sif_precursor"])
            adj.resolved_primary_hazard = resolution_dict["resolved_primary_hazard"]
            adj.resolved_secondary_hazards = resolution_dict.get("resolved_secondary_hazards")
            adj.resolved_activity = resolution_dict["resolved_activity"]
            adj.resolved_primary_precursor = resolution_dict["resolved_primary_precursor"]
            adj.resolved_precursor_categories = resolution_dict.get("resolved_precursor_categories")
            adj.resolved_life_saving_rule = resolution_dict["resolved_life_saving_rule"]
            adj.resolved_life_saving_rules = resolution_dict.get("resolved_life_saving_rules")
            adj.resolved_barriers = resolution_dict.get("resolved_barriers")
            adj.resolved_evidence_spans = resolution_dict.get("resolved_evidence_spans")
            adj.adjudication_notes = resolution_dict["adjudication_notes"]
            adj.adjudicated_at = now

        # Mark all disagreements as RESOLVED
        for d in task.disagreements:
            d.status = "RESOLVED"
            d.resolution_notes = resolution_dict["adjudication_notes"]

        task.status = "ADJUDICATED"
        await self.db.commit()
        await self.db.refresh(adj)
        return adj

    async def get_paired_completed_submissions(
        self,
        batch_id: Optional[str] = None,
    ) -> List[Tuple[AnnotationTask, AnnotationSubmissionRecord, AnnotationSubmissionRecord]]:
        """Fetch pairs of finalized submissions where both Annotator A and B completed."""
        stmt = (
            select(AnnotationTask)
            .options(
                joinedload(AnnotationTask.report),
                selectinload(AnnotationTask.assignments).joinedload(AnnotationAssignment.submission),
            )
            .where(AnnotationTask.status.in_(["COMPLETED", "DISAGREEMENT", "ADJUDICATED"]))
        )
        if batch_id:
            stmt = stmt.where(
                or_(
                    AnnotationTask.batch_id == batch_id,
                    AnnotationTask.batch.has(AnnotationBatch.batch_id == batch_id),
                )
            )

        res = await self.db.execute(stmt)
        tasks = res.scalars().all()
        pairs = []

        for t in tasks:
            subs = [a.submission for a in t.assignments if a.submission and not a.submission.is_draft]
            if len(subs) >= 2:
                # Find slot A and slot B
                sub_a = next((a.submission for a in t.assignments if a.role_slot == "ANNOTATOR_A" and a.submission), None)
                sub_b = next((a.submission for a in t.assignments if a.role_slot == "ANNOTATOR_B" and a.submission), None)
                if sub_a and sub_b:
                    pairs.append((t, sub_a, sub_b))

        return pairs
