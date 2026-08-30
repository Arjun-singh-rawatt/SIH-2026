"""SIFT AI Schemas Package.

Reusable Pydantic models for data contracts, versioned taxonomies,
JSONL dataset schemas, and model inference payloads.
"""

from app.schemas.ai.taxonomy import (
    SIFPotentialLevel,
    SIFPrecursorFlag,
    PrecursorCategory,
    PrimaryHazardType,
    ActivityCategory,
    LifeSavingRuleIdentifier,
    SafetyBarrierCategory,
    BarrierStatusLevel,
    TaxonomyItemDefinition,
)
from app.schemas.ai.dataset import (
    DatasetEvidenceSpan,
    DatasetBarrierAssessment,
    DatasetContext,
    DatasetLabels,
    DatasetAnnotationMetadata,
    DatasetRecord,
)
from app.schemas.ai.contract import (
    ModelInferenceRequest,
    ModelConfidenceBreakdown,
    UrgencyScoreBreakdown,
    ModelInferenceResult,
)

__all__ = [
    "SIFPotentialLevel",
    "SIFPrecursorFlag",
    "PrecursorCategory",
    "PrimaryHazardType",
    "ActivityCategory",
    "LifeSavingRuleIdentifier",
    "SafetyBarrierCategory",
    "BarrierStatusLevel",
    "TaxonomyItemDefinition",
    "DatasetEvidenceSpan",
    "DatasetBarrierAssessment",
    "DatasetContext",
    "DatasetLabels",
    "DatasetAnnotationMetadata",
    "DatasetRecord",
    "ModelInferenceRequest",
    "ModelConfidenceBreakdown",
    "UrgencyScoreBreakdown",
    "ModelInferenceResult",
]
