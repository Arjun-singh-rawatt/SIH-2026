"""SIFT Data Ingestion & Database Export Engine.

Parses raw data from JSON, JSONL, and CSV sources, maps external schema columns,
evaluates training eligibility, and provides database export capabilities.
"""

import csv
from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


class IngestionRecord(BaseModel):
    """Raw record wrapped with provenance metadata."""
    source_file: str
    source_record_id: str
    ingested_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_eligible: bool = True
    ineligibility_reason: Optional[str] = None
    raw_data: Dict[str, Any]


class DataIngester:
    """Ingests raw observation reports across heterogeneous formats."""

    FIELD_MAPPINGS = {
        "description": "raw_text",
        "report_text": "raw_text",
        "narrative": "raw_text",
        "observation": "raw_text",
        "text": "raw_text",
        "id": "report_id",
        "observation_id": "report_id",
        "site": "facility_id",
        "site_code": "facility_id",
        "site_name": "facility_name",
        "basin": "region",
        "unit": "location",
        "type": "report_type",
        "observation_type": "report_type",
    }

    @classmethod
    def normalize_keys(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize raw incoming field names to canonical SIFT keys."""
        normalized = {}
        for k, v in data.items():
            canonical_key = cls.FIELD_MAPPINGS.get(k.lower(), k)
            normalized[canonical_key] = v
        return normalized

    def ingest_file(self, filepath: str) -> List[IngestionRecord]:
        """Ingest records from a file (JSON, JSONL, or CSV)."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Source file not found: {filepath}")

        ext = os.path.splitext(filepath)[1].lower()
        if ext == ".jsonl":
            return self.ingest_jsonl(filepath)
        elif ext == ".json":
            return self.ingest_json(filepath)
        elif ext in {".csv", ".tsv"}:
            delimiter = "\t" if ext == ".tsv" else ","
            return self.ingest_csv(filepath, delimiter=delimiter)
        else:
            raise ValueError(f"Unsupported file format '{ext}'. Must be .json, .jsonl, or .csv")

    def ingest_jsonl(self, filepath: str) -> List[IngestionRecord]:
        """Ingest lines from a JSONL file."""
        records: List[IngestionRecord] = []
        with open(filepath, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    norm_data = self.normalize_keys(data)
                    r_id = norm_data.get("report_id", f"REC-L{line_no:05d}")
                    records.append(IngestionRecord(
                        source_file=filepath,
                        source_record_id=str(r_id),
                        raw_data=norm_data,
                    ))
                except Exception as e:
                    records.append(IngestionRecord(
                        source_file=filepath,
                        source_record_id=f"LINE-{line_no}",
                        is_eligible=False,
                        ineligibility_reason=f"JSONL parse error: {str(e)}",
                        raw_data={"raw_line": line},
                    ))
        return records

    def ingest_json(self, filepath: str) -> List[IngestionRecord]:
        """Ingest objects from a JSON file (list or single object)."""
        records: List[IngestionRecord] = []
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            # Single object or wrapped list
            if "records" in data and isinstance(data["records"], list):
                item_list = data["records"]
            elif "data" in data and isinstance(data["data"], list):
                item_list = data["data"]
            else:
                item_list = [data]
        elif isinstance(data, list):
            item_list = data
        else:
            raise ValueError("Root JSON element must be an array or object.")

        for idx, item in enumerate(item_list, 1):
            if isinstance(item, dict):
                norm_data = self.normalize_keys(item)
                r_id = norm_data.get("report_id", f"REC-J{idx:05d}")
                records.append(IngestionRecord(
                    source_file=filepath,
                    source_record_id=str(r_id),
                    raw_data=norm_data,
                ))
            else:
                records.append(IngestionRecord(
                    source_file=filepath,
                    source_record_id=f"ITEM-{idx}",
                    is_eligible=False,
                    ineligibility_reason="JSON item is not an object",
                    raw_data={"item": str(item)},
                ))
        return records

    def ingest_csv(self, filepath: str, delimiter: str = ",") -> List[IngestionRecord]:
        """Ingest rows from a CSV file."""
        records: List[IngestionRecord] = []
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            for row_no, row in enumerate(reader, 1):
                clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
                norm_data = self.normalize_keys(clean_row)
                r_id = norm_data.get("report_id", f"REC-C{row_no:05d}")
                
                # Transform flat CSV fields to canonical nested structures if present
                parsed_dict = self._parse_flat_csv_to_canonical(norm_data)
                
                records.append(IngestionRecord(
                    source_file=filepath,
                    source_record_id=str(r_id),
                    raw_data=parsed_dict,
                ))
        return records

    def _parse_flat_csv_to_canonical(self, flat: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a flat CSV row dictionary into a canonical SIFT record structure."""
        out = {
            "schema_version": flat.get("schema_version", "1.0"),
            "report_id": flat.get("report_id", ""),
            "raw_text": flat.get("raw_text", ""),
            "report_type": flat.get("report_type", "Near Miss"),
            "context": {
                "facility_id": flat.get("facility_id", "FAC-GEN-01"),
                "facility_name": flat.get("facility_name"),
                "region": flat.get("region", "Upper Assam Basin"),
                "location": flat.get("location", "Main Operating Area"),
                "activity": flat.get("activity", "Maintenance"),
            },
            "labels": {
                "sif_potential": flat.get("sif_potential", "NON-SIF"),
                "sif_precursor": flat.get("sif_precursor", "NO"),
                "primary_precursor": flat.get("primary_precursor", "Procedural Safety"),
                "secondary_precursors": [p.strip() for p in flat.get("secondary_precursors", "").split(";") if p.strip()] if flat.get("secondary_precursors") else [],
                "primary_hazard": flat.get("primary_hazard", "Operational Hazard Exposure"),
                "life_saving_rule": flat.get("life_saving_rule", "Work Authorization & PTW"),
                "barriers": [],
                "evidence_spans": [],
                "urgency_score": int(flat.get("urgency_score", 0)) if str(flat.get("urgency_score", "0")).isdigit() else 0,
                "potential_consequence": flat.get("potential_consequence"),
                "ai_explanation": flat.get("ai_explanation"),
            },
            "annotation": {
                "annotator_id": flat.get("annotator_id", "CSV_IMPORT"),
                "adjudicator_id": flat.get("adjudicator_id"),
                "review_status": flat.get("review_status", "ADJUDICATED"),
                "taxonomy_version": flat.get("taxonomy_version", "1.0"),
                "annotated_at": flat.get("annotated_at") or datetime.now(timezone.utc).isoformat(),
                "disagreement_notes": flat.get("disagreement_notes"),
            },
        }
        
        # If evidence phrase is provided in CSV, calculate character offsets
        ev_phrase = flat.get("evidence_phrase")
        if ev_phrase and ev_phrase in out["raw_text"]:
            start = out["raw_text"].find(ev_phrase)
            out["labels"]["evidence_spans"].append({
                "text": ev_phrase,
                "start_offset": start,
                "end_offset": start + len(ev_phrase),
            })
            
        return out


class DatabaseExporter:
    """Exports reviewed records from SQLite/PostgreSQL SafetyReport models into canonical JSONL."""

    @staticmethod
    def evaluate_training_eligibility(report_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Determine whether a database report is eligible for gold-standard ML training."""
        raw_text = report_dict.get("raw_report_text") or report_dict.get("raw_text")
        if not raw_text or len(raw_text.strip()) < 5:
            return False, "Raw narrative text is missing or too short (< 5 chars)"

        review_status = str(report_dict.get("review_status", "")).upper()
        if review_status not in {"ADJUDICATED", "CONSENSUS_ACCEPTED", "APPROVED"}:
            return False, f"Ineligible review status '{review_status}': Human specialist sign-off is required"

        final_sif = report_dict.get("final_sif_potential")
        if not final_sif:
            return False, "Final human-adjudicated SIF potential is missing"

        return True, None

    @classmethod
    def transform_db_report_to_canonical(
        cls,
        report_dict: Dict[str, Any],
        is_demo: bool = False,
    ) -> Dict[str, Any]:
        """Convert a database report dictionary into canonical DatasetRecord JSON format."""
        raw = report_dict.get("raw_report_text") or report_dict.get("raw_text", "")
        
        # Determine labels from final review if present, or demo fallback
        sif_potential = report_dict.get("final_sif_potential") or report_dict.get("ai_sif_potential", "NON-SIF")
        sif_precursor = report_dict.get("final_sif_precursor") or report_dict.get("ai_sif_precursor", "NO")
        lsr = report_dict.get("final_life_saving_rule") or report_dict.get("ai_life_saving_rule", "Work Authorization & PTW")
        failed_barrier = report_dict.get("final_failed_barrier") or report_dict.get("ai_failed_barrier")
        barrier_status = report_dict.get("final_barrier_status") or report_dict.get("ai_barrier_status", "FAILED")
        
        barriers = []
        if failed_barrier:
            barriers.append({
                "barrier_name": failed_barrier,
                "status": barrier_status,
                "barrier_type": "Engineering / Physical Barrier",
                "description": report_dict.get("reviewer_notes"),
            })

        evidence_spans = []
        ev_phrase = report_dict.get("ai_evidence_phrase")
        if ev_phrase and ev_phrase in raw:
            s_idx = raw.find(ev_phrase)
            evidence_spans.append({
                "text": ev_phrase,
                "start_offset": s_idx,
                "end_offset": s_idx + len(ev_phrase),
            })

        annotator_id = report_dict.get("reviewer_id") or ("DEMO_SEED_USER" if is_demo else "SYSTEM_EXPORT")
        review_status = "ADJUDICATED" if is_demo else report_dict.get("review_status", "PENDING")

        return {
            "schema_version": "1.0",
            "report_id": report_dict.get("report_id", "SIF-2026-00000"),
            "raw_text": raw,
            "report_type": report_dict.get("report_type", "Near Miss"),
            "context": {
                "facility_id": report_dict.get("facility_id", "FAC-DUL-01"),
                "facility_name": report_dict.get("facility_name"),
                "region": report_dict.get("region", "Upper Assam Basin"),
                "location": report_dict.get("location", "Skid Area"),
                "activity": report_dict.get("activity", "Maintenance"),
            },
            "labels": {
                "sif_potential": sif_potential,
                "sif_precursor": sif_precursor,
                "primary_precursor": report_dict.get("ai_precursor_category", "Procedural Safety"),
                "secondary_precursors": [],
                "primary_hazard": report_dict.get("ai_primary_hazard", "Operational Hazard Exposure"),
                "secondary_hazards": [],
                "life_saving_rule": lsr,
                "barriers": barriers,
                "evidence_spans": evidence_spans,
                "urgency_score": int(report_dict.get("ai_urgency_score", 50)),
                "potential_consequence": report_dict.get("potential_consequence"),
                "ai_explanation": report_dict.get("ai_explanation"),
            },
            "annotation": {
                "annotator_id": annotator_id,
                "adjudicator_id": report_dict.get("reviewer_id"),
                "review_status": review_status,
                "taxonomy_version": "1.0",
                "annotated_at": datetime.now(timezone.utc).isoformat(),
                "disagreement_notes": report_dict.get("reviewer_notes"),
            },
        }
