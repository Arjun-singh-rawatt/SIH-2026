"""SIFT Human Annotation Workbench Endpoints.

Provides endpoints for double-blind human annotation, draft management,
dual-annotator agreement auditing, expert adjudication, and release readiness.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_annotation_service, get_current_user
from app.db.models.user import User
from app.services.annotation_service import AnnotationService
from app.schemas.annotation import (
    AnnotationBatchRead,
    AnnotationBatchCreate,
    AnnotationTaskRead,
    AnnotationTaskDetail,
    AnnotationDraftRequest,
    AnnotationSubmitRequest,
    AnnotationSubmissionRead,
    DisagreementRead,
    DisagreementDetail,
    AdjudicationRequest,
    AdjudicationRead,
    AnnotationQualityReport,
    ReleaseReadinessReport,
    TaxonomyReferenceData,
)

router = APIRouter(prefix="/annotations", tags=["Annotation Workbench"])


@router.get(
    "/batches",
    response_model=List[AnnotationBatchRead],
    summary="List Annotation Batches",
)
async def list_batches(
    service: AnnotationService = Depends(get_annotation_service),
) -> List[AnnotationBatchRead]:
    """Retrieve all human annotation batches with computed progress metrics."""
    return await service.list_batches()


@router.post(
    "/batches",
    response_model=AnnotationBatchRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create Annotation Batch (Admin Only)",
)
async def create_batch(
    payload: AnnotationBatchCreate,
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> AnnotationBatchRead:
    """Create a new batch, assign dual blind annotators, and schedule observation tasks."""
    return await service.create_batch(payload, current_user=current_user)


@router.get(
    "/batches/{batch_id}",
    response_model=AnnotationBatchRead,
    summary="Get Batch Details",
)
async def get_batch(
    batch_id: str,
    service: AnnotationService = Depends(get_annotation_service),
) -> AnnotationBatchRead:
    """Retrieve metadata and progress counters for a single batch."""
    return await service.get_batch(batch_id)


@router.get(
    "/tasks",
    response_model=List[AnnotationTaskRead],
    summary="List Annotation Tasks",
)
async def list_tasks(
    batch_id: Optional[str] = Query(default=None, description="Filter by batch ID or UUID"),
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> List[AnnotationTaskRead]:
    """Retrieve annotation tasks. Filters strictly to caller's assignments if caller is an annotator."""
    return await service.get_tasks(batch_id=batch_id, current_user=current_user)


@router.get(
    "/tasks/{task_id}",
    response_model=AnnotationTaskDetail,
    summary="Get Task Narrative & Work State (Blind)",
)
async def get_task_detail(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> AnnotationTaskDetail:
    """Fetch safety report narrative for independent annotation.
    
    CRITICAL BLINDNESS ENFORCEMENT:
    - Strips all AI prediction columns.
    - Omits peer annotator's work entirely.
    """
    return await service.get_task_detail(task_id=task_id, current_user=current_user)


@router.post(
    "/tasks/{task_id}/draft",
    response_model=AnnotationSubmissionRead,
    summary="Save Private Annotation Draft",
)
async def save_draft(
    task_id: str,
    payload: AnnotationDraftRequest,
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> AnnotationSubmissionRead:
    """Save work-in-progress draft. Draft remains strictly private to the calling annotator."""
    return await service.save_draft(task_id=task_id, payload=payload, current_user=current_user)


@router.post(
    "/tasks/{task_id}/submit",
    response_model=AnnotationSubmissionRead,
    summary="Submit Finalized Human Annotation",
)
async def submit_annotation(
    task_id: str,
    payload: AnnotationSubmitRequest,
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> AnnotationSubmissionRead:
    """Submit final annotation. Triggers dual-annotator agreement check if peer has submitted."""
    return await service.submit_annotation(task_id=task_id, payload=payload, current_user=current_user)


@router.get(
    "/disagreements",
    response_model=List[DisagreementRead],
    summary="List Disagreements Queue (Adjudicator Only)",
)
async def list_disagreements(
    batch_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> List[DisagreementRead]:
    """Retrieve queue of field-level discrepancies requiring Lead HSE Expert resolution."""
    return await service.list_disagreements(batch_id=batch_id, current_user=current_user)


@router.get(
    "/disagreements/{task_id}",
    response_model=DisagreementDetail,
    summary="Get Adjudication Side-by-Side Comparison",
)
async def get_disagreement_detail(
    task_id: str,
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> DisagreementDetail:
    """Retrieve side-by-side comparison of Annotator A vs Annotator B for expert adjudication."""
    return await service.get_disagreement_detail(task_id=task_id, current_user=current_user)


@router.post(
    "/disagreements/{task_id}/adjudicate",
    response_model=AdjudicationRead,
    summary="Resolve Disagreements as Ground Truth",
)
async def adjudicate_task(
    task_id: str,
    payload: AdjudicationRequest,
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> AdjudicationRead:
    """Submit canonical expert resolution, marking task as ADJUDICATED."""
    return await service.adjudicate_task(task_id=task_id, payload=payload, current_user=current_user)


@router.get(
    "/quality",
    response_model=AnnotationQualityReport,
    summary="Inter-Annotator Agreement Quality Metrics",
)
async def get_quality_report(
    batch_id: Optional[str] = Query(default=None),
    service: AnnotationService = Depends(get_annotation_service),
) -> AnnotationQualityReport:
    """Compute Cohen's Kappa, multi-label Jaccard similarity, and evidence span IoU."""
    return await service.get_quality_report(batch_id=batch_id)


@router.get(
    "/release-readiness",
    response_model=ReleaseReadinessReport,
    summary="7 Dataset Release Gates Audit",
)
async def get_release_readiness(
    batch_id: Optional[str] = Query(default=None),
    service: AnnotationService = Depends(get_annotation_service),
) -> ReleaseReadinessReport:
    """Evaluate dataset against all 7 release gates before dataset serialization."""
    return await service.get_release_readiness(batch_id=batch_id)


@router.get(
    "/taxonomy",
    response_model=TaxonomyReferenceData,
    summary="Canonical SIFT Taxonomy Lists",
)
async def get_taxonomy(
    service: AnnotationService = Depends(get_annotation_service),
) -> TaxonomyReferenceData:
    """Retrieve all canonical taxonomy strings for dynamic frontend selectors."""
    return service.get_taxonomy()


@router.post(
    "/demo-seed",
    response_model=AnnotationBatchRead,
    summary="Pre-seed Interactive Demo Batch (BATCH-2026-001)",
)
async def seed_demo_batch(
    current_user: User = Depends(get_current_user),
    service: AnnotationService = Depends(get_annotation_service),
) -> AnnotationBatchRead:
    """Pre-seed sample demo batch from database reports for pipeline validation."""
    return await service.seed_demo_batch(created_by_id=current_user.user_id)
