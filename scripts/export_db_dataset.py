#!/usr/bin/env python3
"""SIFT Database Export CLI.

Exports human-reviewed/adjudicated safety reports from the PostgreSQL / SQLite database
into canonical SIFT DatasetRecord JSONL format with strict training eligibility evaluation.

Usage:
    python scripts/export_db_dataset.py --output data/raw/db_export.jsonl --demo
"""

import argparse
import asyncio
import json
import os
import sys

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.db.models.safety_report import SafetyReport
from app.db.models.barrier_assessment import BarrierAssessment
from data_pipeline.ingestion import DatabaseExporter


async def export_from_database(output_path: str, is_demo: bool = False):
    print(f"[*] Connecting to database session...")
    async with AsyncSessionLocal() as session:
        stmt = select(SafetyReport).options(
            selectinload(SafetyReport.barrier_assessments),
            selectinload(SafetyReport.facility),
        )
        result = await session.execute(stmt)
        reports = result.scalars().all()

    print(f"[*] Found {len(reports)} records in database.")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    eligible_count = 0
    ineligible_count = 0

    with open(output_path, "w", encoding="utf-8") as f:
        for r in reports:
            # Convert SQLAlchemy model to dict
            r_dict = {
                "report_id": r.report_id,
                "raw_report_text": r.raw_report_text,
                "language": r.language,
                "report_type": r.report_type,
                "facility_id": r.facility_id,
                "facility_name": r.facility.name if r.facility else None,
                "region": r.facility.region if r.facility else "Upper Assam Basin",
                "location": r.location,
                "activity": r.activity,
                "potential_consequence": r.potential_consequence,
                "ai_sif_potential": r.ai_sif_potential,
                "ai_sif_precursor": r.ai_sif_precursor,
                "ai_confidence": r.ai_confidence,
                "ai_urgency_score": r.ai_urgency_score,
                "ai_primary_hazard": r.ai_primary_hazard,
                "ai_precursor_category": r.ai_precursor_category,
                "ai_life_saving_rule": r.ai_life_saving_rule,
                "ai_failed_barrier": r.ai_failed_barrier,
                "ai_barrier_status": r.ai_barrier_status,
                "ai_evidence_phrase": r.ai_evidence_phrase,
                "ai_explanation": r.ai_explanation,
                "review_status": r.review_status,
                "reviewer_id": r.reviewer_id,
                "reviewer_notes": r.reviewer_notes,
                "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None,
                "final_sif_potential": r.final_sif_potential,
                "final_sif_precursor": r.final_sif_precursor,
                "final_life_saving_rule": r.final_life_saving_rule,
                "final_failed_barrier": r.final_failed_barrier,
                "final_barrier_status": r.final_barrier_status,
            }

            if is_demo:
                canonical = DatabaseExporter.transform_db_report_to_canonical(r_dict, is_demo=True)
                f.write(json.dumps(canonical, ensure_ascii=False) + "\n")
                eligible_count += 1
            else:
                is_eligible, reason = DatabaseExporter.evaluate_training_eligibility(r_dict)
                if is_eligible:
                    canonical = DatabaseExporter.transform_db_report_to_canonical(r_dict, is_demo=False)
                    f.write(json.dumps(canonical, ensure_ascii=False) + "\n")
                    eligible_count += 1
                else:
                    ineligible_count += 1
                    print(f"[!] Report {r.report_id} ineligible: {reason}")

    print("\n" + "=" * 50)
    print("DATABASE EXPORT SUMMARY")
    print("=" * 50)
    print(f"Export Mode:       {'DEMO DATASET EXPORT' if is_demo else 'GOLD GROUND TRUTH EXPORT'}")
    print(f"Eligible Exported: {eligible_count}")
    print(f"Ineligible/Skipped:{ineligible_count}")
    print(f"Destination:       {output_path}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Export eligible safety records from database.")
    parser.add_argument("--output", "-o", default="data/raw/database_export.jsonl", help="Output .jsonl path")
    parser.add_argument("--demo", action="store_true", help="Export as DEMO DATASET (transforms demo seed records)")
    
    args = parser.parse_args()
    asyncio.run(export_from_database(args.output, is_demo=args.demo))


if __name__ == "__main__":
    main()
