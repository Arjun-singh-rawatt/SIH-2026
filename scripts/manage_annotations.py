#!/usr/bin/env python3
"""SIFT Human Annotation Lifecycle, Batch Management & Adjudication CLI.

Supports:
1. Annotation Batch Creation (partitions observations and tracks batch lifecycle)
2. Double-Blind Task Export (strips all AI predictions to eliminate bias)
3. Multi-Faceted Inter-Annotator Agreement Audit (Kappa, Jaccard, span IoU)
4. Disagreement Reporting (generates ADJUDICATION_REQUIRED items)
5. Lead Expert Adjudication Application

Usage:
    python scripts/manage_annotations.py create-batch --batch-id BATCH-2026-001 --source-id SRC-OIL-2026-01 --input data/interim/source.jsonl --output-tasks data/annotations/batch_001_tasks.jsonl
    python scripts/manage_annotations.py audit --annotator-a data/annotations/sub_a.jsonl --annotator-b data/annotations/sub_b.jsonl --output-consensus data/validated/consensus.jsonl --output-disagreements data/annotations/disagreements.json
"""

import argparse
import json
import os
import sys
from typing import List, Optional

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from data_pipeline.annotations import (
    AnnotationManager,
    AnnotationSubmission,
    AdjudicationRecord,
)
from data_pipeline.batches import BatchManager, BatchStatus


def run_create_batch(args):
    print(f"[*] Creating annotation batch: {args.batch_id} for source: {args.source_id}")
    reports = []
    report_ids = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                d = json.loads(line)
                reports.append(d)
                report_ids.append(d.get("report_id", f"REC-{len(report_ids)+1}"))

    batch_mgr = BatchManager(args.batch_dir)
    annotators = args.annotators.split(",") if args.annotators else ["HSE-ANN-01", "HSE-ANN-02"]
    
    meta = batch_mgr.create_batch(
        batch_id=args.batch_id,
        source_id=args.source_id,
        report_ids=report_ids,
        annotator_ids=annotators,
        notes=args.notes,
    )

    # Export tasks
    if args.output_tasks:
        mgr = AnnotationManager()
        tasks = mgr.export_double_blind_batch(reports)
        os.makedirs(os.path.dirname(os.path.abspath(args.output_tasks)), exist_ok=True)
        with open(args.output_tasks, "w", encoding="utf-8") as f:
            for t in tasks:
                f.write(json.dumps(t, ensure_ascii=False) + "\n")
        batch_mgr.update_status(args.batch_id, BatchStatus.EXPORTED)
        print(f"[✓] Exported {len(tasks)} double-blind tasks to: {args.output_tasks}")

    print(f"[✓] Created batch record: {meta.batch_id} ({len(report_ids)} records, status: {meta.status.value})")


def run_export(args):
    print(f"[*] Exporting double-blind annotation tasks from: {args.input}")
    reports = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                reports.append(json.loads(line))

    mgr = AnnotationManager()
    tasks = mgr.export_double_blind_batch(reports)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    print(f"[✓] Exported {len(tasks)} bias-free annotation tasks to: {args.output}")


def load_submissions(filepath: str) -> List[AnnotationSubmission]:
    subs = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                subs.append(AnnotationSubmission(**data))
    return subs


def run_audit(args):
    print(f"[*] Auditing paired annotations:")
    print(f"  - Annotator A: {args.annotator_a}")
    print(f"  - Annotator B: {args.annotator_b}")

    subs_a = load_submissions(args.annotator_a)
    subs_b = load_submissions(args.annotator_b)

    mgr = AnnotationManager()
    rep, consensus = mgr.audit_inter_annotator_agreement(subs_a, subs_b)

    print("\n" + "=" * 60)
    print(" MULTI-FACETED INTER-ANNOTATOR AGREEMENT AUDIT")
    print("=" * 60)
    print(f"Paired Records:             {rep.total_paired_records}")
    print(f"Unanimous Consensus:        {rep.unanimous_consensus_count}")
    print(f"Discrepancies Flagged:      {rep.discrepancy_count}")
    print(f"SIF Potential Agreement:    {rep.sif_potential_agreement_pct}%")
    print(f"Precursor Category Agree:   {rep.precursor_category_agreement_pct}%")
    print(f"Primary Hazard Agreement:   {rep.primary_hazard_agreement_pct}%")
    print(f"Life-Saving Rule Agree:     {rep.life_saving_rule_agreement_pct}%")
    print(f"Multilabel Precursor Jaccard: {rep.multilabel_precursor_jaccard:.4f}")
    print(f"Evidence Span Mean IoU:     {rep.evidence_span_iou:.4f}")
    print(f"Overall Cohen's Kappa:      {rep.overall_cohens_kappa:.4f}")
    print("=" * 60)

    if rep.requires_adjudication_ids:
        print(f"\n[!] {len(rep.requires_adjudication_ids)} Records Require Lead Adjudication:")
        for r_id in rep.requires_adjudication_ids:
            print(f"  - {r_id}")

    if args.output_consensus and consensus:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_consensus)), exist_ok=True)
        with open(args.output_consensus, "w", encoding="utf-8") as f:
            for c in consensus:
                f.write(json.dumps(c, ensure_ascii=False) + "\n")
        print(f"\n[✓] Saved {len(consensus)} consensus records to: {args.output_consensus}")

    if args.output_disagreements and rep.disagreements:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_disagreements)), exist_ok=True)
        with open(args.output_disagreements, "w", encoding="utf-8") as f:
            payload = [d.model_dump() for d in rep.disagreements]
            json.dump(payload, f, indent=2)
        print(f"[✓] Saved {len(rep.disagreements)} disagreement items to: {args.output_disagreements}")

    if args.batch_id:
        batch_mgr = BatchManager()
        st = BatchStatus.COMPLETED if rep.discrepancy_count == 0 else BatchStatus.UNDER_REVIEW
        batch_mgr.update_status(
            args.batch_id,
            st,
            completed_submissions_count=rep.total_paired_records,
            discrepancy_count=rep.discrepancy_count,
        )


def run_adjudicate(args):
    print(f"[*] Applying expert adjudication:")
    print(f"  - Discrepant/Base records: {args.base_reports}")
    print(f"  - Adjudication file:       {args.adjudications}")

    base_map = {}
    with open(args.base_reports, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                base_map[d.get("report_id")] = d

    adjudications = []
    with open(args.adjudications, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                adjudications.append(AdjudicationRecord(**json.loads(line)))

    mgr = AnnotationManager()
    resolved_records = []
    for adj in adjudications:
        base = base_map.get(adj.report_id, {"report_id": adj.report_id})
        res = mgr.apply_adjudication(base, adj)
        resolved_records.append(res)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        for r in resolved_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"[✓] Resolved {len(resolved_records)} records into ADJUDICATED state at: {args.output}")


def run_list_batches(args):
    batch_mgr = BatchManager(args.batch_dir)
    batches = batch_mgr.list_batches()
    print("\n" + "=" * 70)
    print(" SIFT ANNOTATION BATCHES")
    print("=" * 70)
    if not batches:
        print(" No annotation batches created yet.")
    else:
        for b in batches:
            print(f"[{b.batch_id}] Source: {b.source_id} | Records: {b.record_count} | Status: {b.status.value}")
            print(f"  Annotators: {', '.join(b.annotator_ids)} | Discrepancies: {b.discrepancy_count}")
            print("-" * 70)


def main():
    parser = argparse.ArgumentParser(description="Manage SIFT human annotations and expert adjudication.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create Batch
    p_batch = subparsers.add_parser("create-batch", help="Create an annotation batch from interim reports")
    p_batch.add_argument("--batch-id", "-b", required=True, help="Unique batch identifier, e.g. BATCH-2026-001")
    p_batch.add_argument("--source-id", "-s", required=True, help="Registered source ID")
    p_batch.add_argument("--input", "-i", required=True, help="Input normalized reports JSONL")
    p_batch.add_argument("--output-tasks", "-o", help="Optional path to write double-blind tasks")
    p_batch.add_argument("--annotators", "-a", help="Comma-separated annotator IDs (default: HSE-ANN-01,HSE-ANN-02)")
    p_batch.add_argument("--batch-dir", default="data/metadata/annotation_batches")
    p_batch.add_argument("--notes", help="Optional batch description")

    # Export Subcommand
    p_export = subparsers.add_parser("export", help="Export reports for double-blind annotation")
    p_export.add_argument("--input", "-i", required=True, help="Input raw or unannotated reports file")
    p_export.add_argument("--output", "-o", required=True, help="Output double-blind tasks file")

    # Audit Subcommand
    p_audit = subparsers.add_parser("audit", help="Audit paired annotator submissions and calculate agreement")
    p_audit.add_argument("--annotator-a", "-a", required=True, help="Submission file from Annotator A")
    p_audit.add_argument("--annotator-b", "-b", required=True, help="Submission file from Annotator B")
    p_audit.add_argument("--output-consensus", "-o", help="Optional output path for consensus-accepted records")
    p_audit.add_argument("--output-disagreements", "-d", help="Optional output path for disagreement items JSON")
    p_audit.add_argument("--batch-id", help="Optional batch ID to update state")

    # Adjudicate Subcommand
    p_adj = subparsers.add_parser("adjudicate", help="Apply expert adjudication to resolve discrepancies")
    p_adj.add_argument("--base-reports", "-b", required=True, help="Base reports JSONL")
    p_adj.add_argument("--adjudications", "-a", required=True, help="Lead adjudicator records JSONL")
    p_adj.add_argument("--output", "-o", required=True, help="Output resolved dataset records JSONL")

    # List Batches
    p_list = subparsers.add_parser("list-batches", help="List all annotation batches")
    p_list.add_argument("--batch-dir", default="data/metadata/annotation_batches")

    args = parser.parse_args()

    if args.command == "create-batch":
        run_create_batch(args)
    elif args.command == "export":
        run_export(args)
    elif args.command == "audit":
        run_audit(args)
    elif args.command == "adjudicate":
        run_adjudicate(args)
    elif args.command == "list-batches":
        run_list_batches(args)


if __name__ == "__main__":
    main()
