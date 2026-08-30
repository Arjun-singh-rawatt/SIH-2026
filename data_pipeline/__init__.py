"""SIFT Data Engineering, Acquisition, Governance & Annotation Pipeline.

Provides deterministic normalization, governance/PII protection, canonical schema validation,
double-blind annotation workflows, multi-faceted agreement audits, lead adjudication,
deduplication, temporal splitting, and cryptographic dataset release packaging.
"""

from data_pipeline.normalization import (
    TextNormalizer,
    normalize_text,
    compute_content_hash,
    recalculate_evidence_offsets,
    normalize_record_text,
)
from data_pipeline.governance import (
    PIIDetector,
    GovernanceChecker,
    PIIMatch,
    PIIResult,
    PIIStatus,
    GovernanceReport,
)
from data_pipeline.validation import (
    DatasetValidator,
    ValidationResult,
    ValidationIssue,
    ValidationSeverity,
)
from data_pipeline.duplicates import (
    DuplicateDetector,
    DuplicateType,
    NearDuplicateMatch,
    DuplicateResult,
)
from data_pipeline.annotations import (
    AnnotationManager,
    AnnotationSubmission,
    AgreementReport,
    AdjudicationRecord,
    DisagreementItem,
    compute_cohens_kappa,
    compute_jaccard_similarity,
    compute_span_iou,
)
from data_pipeline.splitting import (
    DatasetSplitter,
    SplitConfig,
    SplitMetrics,
    SplitResult,
)
from data_pipeline.metrics import (
    DatasetMetricsCalculator,
    DatasetStatistics,
)
from data_pipeline.manifest import (
    DatasetManifestGenerator,
    FileManifestEntry,
    DatasetManifest,
    DatasetMetadata,
    QualityReport,
)
from data_pipeline.ingestion import DataIngester, DatabaseExporter
from data_pipeline.sources import (
    SourceType,
    DataClassification,
    PermissionStatus,
    RegisteredSource,
    SourceProvenance,
    SourceRegistry,
)
from data_pipeline.batches import (
    BatchStatus,
    AnnotationBatchMetadata,
    BatchManager,
)
from data_pipeline.release_gate import (
    ReleaseGateAuditor,
    ReleaseGateReport,
    ReleaseGateCheckItem,
)

# Aliases for backwards compatibility
ValidationReport = ValidationResult

__all__ = [
    "TextNormalizer",
    "normalize_text",
    "compute_content_hash",
    "recalculate_evidence_offsets",
    "normalize_record_text",
    "PIIDetector",
    "GovernanceChecker",
    "PIIMatch",
    "PIIResult",
    "PIIStatus",
    "GovernanceReport",
    "DatasetValidator",
    "ValidationResult",
    "ValidationReport",
    "ValidationIssue",
    "ValidationSeverity",
    "DuplicateDetector",
    "DuplicateType",
    "NearDuplicateMatch",
    "DuplicateResult",
    "AnnotationManager",
    "AnnotationSubmission",
    "AgreementReport",
    "AdjudicationRecord",
    "DisagreementItem",
    "compute_cohens_kappa",
    "compute_jaccard_similarity",
    "compute_span_iou",
    "DatasetSplitter",
    "SplitConfig",
    "SplitMetrics",
    "SplitResult",
    "DatasetMetricsCalculator",
    "DatasetStatistics",
    "DatasetManifestGenerator",
    "FileManifestEntry",
    "DatasetManifest",
    "DatasetMetadata",
    "QualityReport",
    "DataIngester",
    "DatabaseExporter",
    "SourceType",
    "DataClassification",
    "PermissionStatus",
    "RegisteredSource",
    "SourceProvenance",
    "SourceRegistry",
    "BatchStatus",
    "AnnotationBatchMetadata",
    "BatchManager",
    "ReleaseGateAuditor",
    "ReleaseGateReport",
    "ReleaseGateCheckItem",
]
