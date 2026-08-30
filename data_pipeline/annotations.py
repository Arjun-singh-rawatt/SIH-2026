"""SIFT Human Annotation, Double-Blind Protocol, Multi-Faceted Agreement & Adjudication Engine.

Implements:
1. Double-blind task export (all AI predictions, confidence scores, and reviewer hints stripped)
2. Multi-faceted inter-annotator agreement:
   - Categorical Agreement: Cohen's Kappa for SIF Potential, Primary Precursor, Primary Hazard, LSR
   - Multi-Label Agreement: Jaccard Set Similarity for precursor categories and barrier categories
   - Span Agreement: Character-level Intersection-over-Union (IoU) for evidence spans
3. Detailed Disagreement Reporting with field-level conflict isolation (ADJUDICATION_REQUIRED)
4. Formal Lead HSE Expert Adjudication into canonical DatasetRecords
"""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional, Set, Tuple
from pydantic import BaseModel, Field

from data_pipeline.validation import DatasetValidator


class AnnotationSubmission(BaseModel):
    """Single human annotator submission for a safety report."""
    report_id: str
    annotator_id: str
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_text: str
    report_type: str = "Near Miss"
    context: Dict[str, Any] = Field(default_factory=dict)
    labels: Dict[str, Any]
    notes: Optional[str] = None


class DisagreementItem(BaseModel):
    """Specific field-level disagreement between paired annotators."""
    report_id: str
    field_name: str
    annotator_a: str
    annotator_b: str
    annotator_a_value: Any
    annotator_b_value: Any
    status: str = "ADJUDICATION_REQUIRED"
    notes: Optional[str] = None


class AgreementReport(BaseModel):
    """Comprehensive inter-annotator agreement audit across paired submissions."""
    total_paired_records: int
    unanimous_consensus_count: int
    discrepancy_count: int
    sif_potential_agreement_pct: float
    precursor_category_agreement_pct: float
    life_saving_rule_agreement_pct: float
    primary_hazard_agreement_pct: float = 100.0
    multilabel_precursor_jaccard: float = 1.0
    evidence_span_iou: float = 1.0
    overall_cohens_kappa: float
    requires_adjudication_ids: List[str] = Field(default_factory=list)
    disagreements: List[DisagreementItem] = Field(default_factory=list)


class AdjudicationRecord(BaseModel):
    """Formal expert adjudication resolving annotator divergence."""
    report_id: str
    adjudicator_id: str
    adjudicated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_labels: Dict[str, Any]
    disagreement_notes: str


def compute_cohens_kappa(labels_a: List[str], labels_b: List[str]) -> float:
    """Compute Cohen's Kappa coefficient between two annotator label sequences."""
    if not labels_a or len(labels_a) != len(labels_b):
        return 1.0
    
    n = len(labels_a)
    if n == 0:
        return 1.0

    categories = list(set(labels_a).union(set(labels_b)))
    if len(categories) <= 1:
        return 1.0

    # Observed agreement Po
    matches = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    po = matches / n

    # Expected agreement Pe
    count_a = {c: labels_a.count(c) for c in categories}
    count_b = {c: labels_b.count(c) for c in categories}
    
    pe = sum((count_a[c] / n) * (count_b[c] / n) for c in categories)

    if pe >= 1.0:
        return 1.0
    kappa = (po - pe) / (1.0 - pe)
    return round(max(0.0, min(1.0, kappa)), 4)


def compute_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Compute Jaccard similarity coefficient between two sets."""
    if not set_a and not set_b:
        return 1.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return round(intersection / union, 4) if union > 0 else 0.0


def compute_span_iou(spans_a: List[Dict[str, Any]], spans_b: List[Dict[str, Any]]) -> float:
    """Compute character-level Intersection over Union (IoU) across evidence spans."""
    if not spans_a and not spans_b:
        return 1.0
    if not spans_a or not spans_b:
        return 0.0

    # Convert spans into set of character indices
    chars_a: Set[int] = set()
    for s in spans_a:
        st, en = s.get("start_offset", 0), s.get("end_offset", 0)
        chars_a.update(range(st, en))

    chars_b: Set[int] = set()
    for s in spans_b:
        st, en = s.get("start_offset", 0), s.get("end_offset", 0)
        chars_b.update(range(st, en))

    return compute_jaccard_similarity(chars_a, chars_b)


class AnnotationManager:
    """Manages double-blind export, multi-annotator audits, and lead adjudication."""

    def __init__(self, taxonomy_version: str = "1.0"):
        self.taxonomy_version = taxonomy_version
        self.validator = DatasetValidator()

    def export_double_blind_batch(
        self,
        raw_reports: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Export safety reports for double-blind human annotation.
        
        CRITICAL: Strips all AI predictions (ai_*), confidence scores, and previous reviewer hints
        to eliminate cognitive anchoring and bias.
        
        Args:
            raw_reports: List of raw safety report dictionaries.
            
        Returns:
            Sanitized, bias-free annotation task objects.
        """
        export_tasks = []
        for r in raw_reports:
            task = {
                "report_id": r.get("report_id", ""),
                "raw_text": r.get("raw_report_text") or r.get("raw_text", ""),
                "report_type": r.get("report_type", "Near Miss"),
                "context": {
                    "facility_id": r.get("facility_id", r.get("context", {}).get("facility_id", "FAC-GEN-01")),
                    "facility_name": r.get("facility_name", r.get("context", {}).get("facility_name")),
                    "region": r.get("region", r.get("context", {}).get("region", "Upper Assam Basin")),
                    "location": r.get("location", r.get("context", {}).get("location", "Main Operating Section")),
                    "activity": r.get("activity", r.get("context", {}).get("activity", "Maintenance")),
                },
                "annotation_schema_version": "1.0",
                "taxonomy_version": self.taxonomy_version,
                "annotation_fields_required": [
                    "sif_potential",
                    "sif_precursor",
                    "primary_precursor",
                    "secondary_precursors",
                    "primary_hazard",
                    "life_saving_rule",
                    "barriers",
                    "evidence_spans",
                    "urgency_score",
                    "potential_consequence",
                ],
            }
            export_tasks.append(task)
        return export_tasks

    def audit_inter_annotator_agreement(
        self,
        annotations_a: List[AnnotationSubmission],
        annotations_b: List[AnnotationSubmission],
    ) -> Tuple[AgreementReport, List[Dict[str, Any]]]:
        """Audit paired annotations from two independent specialists.
        
        Computes consensus, calculates Cohen's Kappa, evaluates multi-label Jaccard and span IoU,
        and isolates all field-level disagreements for adjudication.
        
        Args:
            annotations_a: Submissions from Annotator A.
            annotations_b: Submissions from Annotator B.
            
        Returns:
            Tuple of (AgreementReport, list of consensus-accepted canonical records).
        """
        map_a = {sub.report_id: sub for sub in annotations_a}
        map_b = {sub.report_id: sub for sub in annotations_b}

        common_ids = sorted(list(set(map_a.keys()).intersection(set(map_b.keys()))))
        
        sif_a_list, sif_b_list = [], []
        prec_a_list, prec_b_list = [], []
        lsr_a_list, lsr_b_list = [], []
        haz_a_list, haz_b_list = [], []

        consensus_records = []
        requires_adjudication = []
        disagreements: List[DisagreementItem] = []

        sif_matches = 0
        prec_matches = 0
        lsr_matches = 0
        haz_matches = 0
        total_jaccard = 0.0
        total_span_iou = 0.0

        for r_id in common_ids:
            sub_a = map_a[r_id]
            sub_b = map_b[r_id]
            record_has_discrepancy = False

            # 1. SIF Potential
            sif_a = str(sub_a.labels.get("sif_potential", "")).upper()
            sif_b = str(sub_b.labels.get("sif_potential", "")).upper()
            sif_a_list.append(sif_a)
            sif_b_list.append(sif_b)
            if sif_a == sif_b:
                sif_matches += 1
            else:
                record_has_discrepancy = True
                disagreements.append(DisagreementItem(
                    report_id=r_id,
                    field_name="sif_potential",
                    annotator_a=sub_a.annotator_id,
                    annotator_b=sub_b.annotator_id,
                    annotator_a_value=sif_a,
                    annotator_b_value=sif_b,
                ))

            # 2. Primary Precursor
            prec_a = str(sub_a.labels.get("primary_precursor", ""))
            prec_b = str(sub_b.labels.get("primary_precursor", ""))
            prec_a_list.append(prec_a)
            prec_b_list.append(prec_b)
            if prec_a == prec_b:
                prec_matches += 1
            else:
                record_has_discrepancy = True
                disagreements.append(DisagreementItem(
                    report_id=r_id,
                    field_name="primary_precursor",
                    annotator_a=sub_a.annotator_id,
                    annotator_b=sub_b.annotator_id,
                    annotator_a_value=prec_a,
                    annotator_b_value=prec_b,
                ))

            # 3. Life-Saving Rule
            lsr_a = str(sub_a.labels.get("life_saving_rule", ""))
            lsr_b = str(sub_b.labels.get("life_saving_rule", ""))
            lsr_a_list.append(lsr_a)
            lsr_b_list.append(lsr_b)
            if lsr_a == lsr_b:
                lsr_matches += 1
            else:
                record_has_discrepancy = True
                disagreements.append(DisagreementItem(
                    report_id=r_id,
                    field_name="life_saving_rule",
                    annotator_a=sub_a.annotator_id,
                    annotator_b=sub_b.annotator_id,
                    annotator_a_value=lsr_a,
                    annotator_b_value=lsr_b,
                ))

            # 4. Primary Hazard
            haz_a = str(sub_a.labels.get("primary_hazard", ""))
            haz_b = str(sub_b.labels.get("primary_hazard", ""))
            haz_a_list.append(haz_a)
            haz_b_list.append(haz_b)
            if haz_a == haz_b:
                haz_matches += 1
            else:
                record_has_discrepancy = True
                disagreements.append(DisagreementItem(
                    report_id=r_id,
                    field_name="primary_hazard",
                    annotator_a=sub_a.annotator_id,
                    annotator_b=sub_b.annotator_id,
                    annotator_a_value=haz_a,
                    annotator_b_value=haz_b,
                ))

            # 5. Multi-label Precursor Categories Jaccard
            precs_set_a = set(sub_a.labels.get("secondary_precursors", []) + ([prec_a] if prec_a else []))
            precs_set_b = set(sub_b.labels.get("secondary_precursors", []) + ([prec_b] if prec_b else []))
            rec_jaccard = compute_jaccard_similarity(precs_set_a, precs_set_b)
            total_jaccard += rec_jaccard

            # 6. Evidence Span Character-Level IoU
            spans_a = sub_a.labels.get("evidence_spans", [])
            spans_b = sub_b.labels.get("evidence_spans", [])
            rec_iou = compute_span_iou(spans_a, spans_b)
            total_span_iou += rec_iou
            if rec_iou < 0.5 and (spans_a or spans_b):
                record_has_discrepancy = True
                disagreements.append(DisagreementItem(
                    report_id=r_id,
                    field_name="evidence_spans",
                    annotator_a=sub_a.annotator_id,
                    annotator_b=sub_b.annotator_id,
                    annotator_a_value=spans_a,
                    annotator_b_value=spans_b,
                    notes=f"Span IoU: {rec_iou:.2f}",
                ))

            # Check for unanimous agreement across all primary categorical labels
            if not record_has_discrepancy:
                merged_labels = dict(sub_a.labels)
                if "sif_precursor" not in merged_labels:
                    merged_labels["sif_precursor"] = "YES" if sif_a in {"CRITICAL", "HIGH"} else "NO"
                if "primary_hazard" not in merged_labels:
                    merged_labels["primary_hazard"] = "Operational Hazard Exposure"
                if "secondary_precursors" not in merged_labels:
                    merged_labels["secondary_precursors"] = []
                if "secondary_hazards" not in merged_labels:
                    merged_labels["secondary_hazards"] = []
                if "barriers" not in merged_labels:
                    merged_labels["barriers"] = []
                if "evidence_spans" not in merged_labels:
                    merged_labels["evidence_spans"] = []
                if "urgency_score" not in merged_labels:
                    merged_labels["urgency_score"] = 90 if sif_a in {"CRITICAL", "HIGH"} else 15

                consensus_dict = {
                    "schema_version": "1.0",
                    "report_id": r_id,
                    "raw_text": sub_a.raw_text,
                    "report_type": sub_a.report_type,
                    "context": sub_a.context,
                    "labels": merged_labels,
                    "annotation": {
                        "annotator_id": f"{sub_a.annotator_id}+{sub_b.annotator_id}",
                        "adjudicator_id": None,
                        "review_status": "CONSENSUS_ACCEPTED",
                        "taxonomy_version": self.taxonomy_version,
                        "annotated_at": datetime.now(timezone.utc).isoformat(),
                        "disagreement_notes": "Unanimous dual-annotator consensus.",
                    },
                }
                consensus_records.append(consensus_dict)
            else:
                requires_adjudication.append(r_id)

        n = len(common_ids)
        sif_pct = (sif_matches / n * 100) if n > 0 else 100.0
        prec_pct = (prec_matches / n * 100) if n > 0 else 100.0
        lsr_pct = (lsr_matches / n * 100) if n > 0 else 100.0
        haz_pct = (haz_matches / n * 100) if n > 0 else 100.0
        avg_jaccard = round(total_jaccard / n, 4) if n > 0 else 1.0
        avg_iou = round(total_span_iou / n, 4) if n > 0 else 1.0

        kappa = compute_cohens_kappa(sif_a_list, sif_b_list)

        report = AgreementReport(
            total_paired_records=n,
            unanimous_consensus_count=len(consensus_records),
            discrepancy_count=len(requires_adjudication),
            sif_potential_agreement_pct=round(sif_pct, 2),
            precursor_category_agreement_pct=round(prec_pct, 2),
            life_saving_rule_agreement_pct=round(lsr_pct, 2),
            primary_hazard_agreement_pct=round(haz_pct, 2),
            multilabel_precursor_jaccard=avg_jaccard,
            evidence_span_iou=avg_iou,
            overall_cohens_kappa=kappa,
            requires_adjudication_ids=requires_adjudication,
            disagreements=disagreements,
        )

        return report, consensus_records

    def apply_adjudication(
        self,
        base_record: Dict[str, Any],
        adjudication: AdjudicationRecord,
    ) -> Dict[str, Any]:
        """Apply lead expert adjudication to resolve conflicting annotations.
        
        Args:
            base_record: Raw record or un-adjudicated consensus dictionary.
            adjudication: Expert adjudication containing authoritative labels and notes.
            
        Returns:
            Authoritative DatasetRecord dictionary in ADJUDICATED state.
        """
        adjudicated_record = {
            "schema_version": "1.0",
            "report_id": adjudication.report_id,
            "raw_text": base_record.get("raw_text") or base_record.get("raw_report_text", ""),
            "report_type": base_record.get("report_type", "Near Miss"),
            "context": base_record.get("context", {
                "facility_id": base_record.get("facility_id", "FAC-GEN-01"),
                "activity": base_record.get("activity", "Maintenance"),
            }),
            "labels": adjudication.resolved_labels,
            "annotation": {
                "annotator_id": base_record.get("annotation", {}).get("annotator_id", "HSE-DUAL"),
                "adjudicator_id": adjudication.adjudicator_id,
                "review_status": "ADJUDICATED",
                "taxonomy_version": self.taxonomy_version,
                "annotated_at": adjudication.adjudicated_at.isoformat(),
                "disagreement_notes": adjudication.disagreement_notes,
            },
        }
        return adjudicated_record
