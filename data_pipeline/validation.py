"""SIFT Canonical Validation Engine.

Enforces strict Pydantic schema adherence, exact character-offset evidence verification,
authoritative taxonomy category compliance, and annotation integrity checks.
"""

from enum import Enum
import sys
import os
from typing import Any, Dict, List, Optional, Set
from pydantic import ValidationError

# Ensure api directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from app.schemas.ai.dataset import DatasetRecord
from app.schemas.ai.taxonomy import (
    SIFPotentialLevel,
    SIFPrecursorFlag,
    PrecursorCategory,
    PrimaryHazardType,
    ActivityCategory,
    LifeSavingRuleIdentifier,
    SafetyBarrierCategory,
    BarrierStatusLevel,
)


class ValidationSeverity(str, Enum):
    """Severity of a validation issue."""
    ERROR = "ERROR"
    WARNING = "WARNING"


class ValidationIssue(BaseModel if 'BaseModel' in globals() else object):
    """Individual validation finding."""
    def __init__(
        self,
        severity: ValidationSeverity,
        field: str,
        message: str,
        value: Optional[Any] = None,
    ):
        self.severity = severity
        self.field = field
        self.message = message
        self.value = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity.value,
            "field": self.field,
            "message": self.message,
            "value": str(self.value) if self.value is not None else None,
        }

    def __repr__(self) -> str:
        return f"[{self.severity.value}] {self.field}: {self.message}"


class ValidationResult:
    """Outcome of validating a single record or dataset."""
    def __init__(self, record_id: str):
        self.record_id = record_id
        self.issues: List[ValidationIssue] = []
        self.is_valid: bool = True
        self.has_warnings: bool = False
        self.validated_record: Optional[DatasetRecord] = None

    def add_error(self, field: str, message: str, value: Optional[Any] = None):
        self.issues.append(ValidationIssue(ValidationSeverity.ERROR, field, message, value))
        self.is_valid = False

    def add_warning(self, field: str, message: str, value: Optional[Any] = None):
        self.issues.append(ValidationIssue(ValidationSeverity.WARNING, field, message, value))
        self.has_warnings = True

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.ERROR]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == ValidationSeverity.WARNING]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "is_valid": self.is_valid,
            "has_warnings": self.has_warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [i.to_dict() for i in self.issues],
        }


class DatasetValidator:
    """Authoritative validation engine for SIFT dataset records."""

    CANONICAL_TAXONOMY_VERSION = "1.0"
    CANONICAL_SCHEMA_VERSION = "1.0"

    # Permitted string values for taxonomies
    VALID_SIF_POTENTIALS = {e.value for e in SIFPotentialLevel}
    VALID_SIF_PRECURSORS = {e.value for e in SIFPrecursorFlag}
    VALID_PRECURSORS = {e.value for e in PrecursorCategory}
    VALID_HAZARDS = {e.value for e in PrimaryHazardType}
    VALID_ACTIVITIES = {e.value for e in ActivityCategory}
    VALID_LIFE_SAVING_RULES = {e.value for e in LifeSavingRuleIdentifier}
    VALID_BARRIER_CATEGORIES = {e.value for e in SafetyBarrierCategory}
    VALID_BARRIER_STATUSES = {e.value for e in BarrierStatusLevel}
    
    # Valid review states for final training ground truth
    VALID_GROUND_TRUTH_STATUSES = {"ADJUDICATED", "CONSENSUS_ACCEPTED", "APPROVED"}

    def __init__(self, strict_taxonomy: bool = True):
        self.strict_taxonomy = strict_taxonomy

    def validate_record_dict(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a raw dictionary representation of a DatasetRecord.
        
        Args:
            data: Dictionary containing record fields.
            
        Returns:
            ValidationResult with detailed issue list.
        """
        record_id = data.get("report_id", "UNKNOWN_RECORD")
        result = ValidationResult(record_id=str(record_id))

        # 1. Pydantic Schema Validation
        try:
            record = DatasetRecord(**data)
            result.validated_record = record
        except ValidationError as e:
            for err in e.errors():
                loc = " -> ".join(str(p) for p in err["loc"])
                result.add_error(
                    field=loc,
                    message=err["msg"],
                    value=err.get("input"),
                )
            return result
        except Exception as ex:
            result.add_error(field="schema", message=f"Unexpected parsing error: {str(ex)}")
            return result

        # 2. Schema and Taxonomy Version Checks
        if record.schema_version != self.CANONICAL_SCHEMA_VERSION:
            result.add_error(
                field="schema_version",
                message=f"Schema version '{record.schema_version}' does not match canonical '{self.CANONICAL_SCHEMA_VERSION}'",
                value=record.schema_version,
            )

        if record.annotation.taxonomy_version != self.CANONICAL_TAXONOMY_VERSION:
            result.add_error(
                field="annotation.taxonomy_version",
                message=f"Taxonomy version '{record.annotation.taxonomy_version}' does not match canonical '{self.CANONICAL_TAXONOMY_VERSION}'",
                value=record.annotation.taxonomy_version,
            )

        # 3. Ground Truth Annotation Status
        review_status = record.annotation.review_status.upper()
        if review_status in {"UNANNOTATED", "ADJUDICATION_REQUIRED", "REJECTED", "DISPUTED"}:
            result.add_error(
                field="annotation.review_status",
                message=f"Record has unresolved or incomplete annotation state '{record.annotation.review_status}'",
                value=record.annotation.review_status,
            )

        # 4. Strict Evidence Span Validation
        raw = record.raw_text
        if len(record.labels.evidence_spans) == 0 and record.labels.sif_potential in {
            SIFPotentialLevel.CRITICAL,
            SIFPotentialLevel.HIGH,
        }:
            result.add_warning(
                field="labels.evidence_spans",
                message="High/Critical SIF observation contains zero grounded evidence spans",
            )

        for idx, span in enumerate(record.labels.evidence_spans):
            # Check non-empty
            if not span.text.strip():
                result.add_error(
                    field=f"labels.evidence_spans[{idx}]",
                    message="Evidence span text is empty or whitespace only",
                    value=span.text,
                )
                continue

            # Check bounds
            if span.start_offset < 0:
                result.add_error(
                    field=f"labels.evidence_spans[{idx}].start_offset",
                    message=f"Start offset ({span.start_offset}) cannot be negative",
                    value=span.start_offset,
                )
            if span.end_offset > len(raw):
                result.add_error(
                    field=f"labels.evidence_spans[{idx}].end_offset",
                    message=f"End offset ({span.end_offset}) exceeds raw_text length ({len(raw)})",
                    value=span.end_offset,
                )
            elif span.end_offset <= span.start_offset:
                result.add_error(
                    field=f"labels.evidence_spans[{idx}]",
                    message=f"End offset ({span.end_offset}) must be > start offset ({span.start_offset})",
                )
            else:
                extracted = raw[span.start_offset:span.end_offset]
                if extracted != span.text:
                    result.add_error(
                        field=f"labels.evidence_spans[{idx}]",
                        message=f"Exact text mismatch: expected '{span.text}', but slice is '{extracted}'",
                        value={"expected": span.text, "found": extracted},
                    )

        # 5. Taxonomy Validation
        if self.strict_taxonomy:
            # Primary Precursor
            if record.labels.primary_precursor.value not in self.VALID_PRECURSORS:
                result.add_error(
                    field="labels.primary_precursor",
                    message=f"Unknown precursor category '{record.labels.primary_precursor.value}'",
                    value=record.labels.primary_precursor.value,
                )
            # Secondary Precursors
            for s_idx, sec in enumerate(record.labels.secondary_precursors):
                if sec.value not in self.VALID_PRECURSORS:
                    result.add_error(
                        field=f"labels.secondary_precursors[{s_idx}]",
                        message=f"Unknown secondary precursor category '{sec.value}'",
                        value=sec.value,
                    )
            # Primary Hazard
            if record.labels.primary_hazard not in self.VALID_HAZARDS:
                result.add_warning(
                    field="labels.primary_hazard",
                    message=f"Hazard '{record.labels.primary_hazard}' not in standard PrimaryHazardType enum",
                    value=record.labels.primary_hazard,
                )
            # Life Saving Rule
            if record.labels.life_saving_rule not in self.VALID_LIFE_SAVING_RULES:
                result.add_warning(
                    field="labels.life_saving_rule",
                    message=f"Life-Saving Rule '{record.labels.life_saving_rule}' not in standard LSR enum",
                    value=record.labels.life_saving_rule,
                )
            # Activity
            if record.context.activity not in self.VALID_ACTIVITIES:
                result.add_warning(
                    field="context.activity",
                    message=f"Activity '{record.context.activity}' not in standard ActivityCategory enum",
                    value=record.context.activity,
                )

        # 6. Barrier Validation
        for b_idx, barrier in enumerate(record.labels.barriers):
            if not barrier.barrier_name.strip():
                result.add_error(
                    field=f"labels.barriers[{b_idx}].barrier_name",
                    message="Barrier name cannot be empty",
                )
            if barrier.status.value not in self.VALID_BARRIER_STATUSES:
                result.add_error(
                    field=f"labels.barriers[{b_idx}].status",
                    message=f"Invalid barrier status '{barrier.status.value}'",
                    value=barrier.status.value,
                )

        return result

    def validate_record(self, record: Any) -> ValidationResult:
        """Validate a DatasetRecord instance or raw record dictionary."""
        if isinstance(record, dict):
            return self.validate_record_dict(record)
        return self.validate_record_dict(record.model_dump(mode="json"))
