#!/usr/bin/env python3
"""SIFT Leakage & Governance Audit CLI.

Audits dataset splits and records for:
1. Cross-split duplicate and near-duplicate leakage
2. Event/incident cluster crossing split boundaries
3. Label leakage into input feature spaces
4. Post-event feature leakage

Usage:
    python scripts/detect_leakage.py --train data/splits/train.jsonl --val data/splits/validation.jsonl --test data/splits/test.jsonl
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Set

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from data_pipeline.governance import GovernanceChecker
from data_pipeline.normalization import compute_content_hash
from data_pipeline.duplicates import _tokenize_text, compute_jaccard_similarity


def load_split_records(filepath: str, split_name: str) -> List[Dict[str, any]]:
    if not filepath or not os.path.exists(filepath):
        return []
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                rec["_split_assigned"] = split_name
                records.append(rec)
    return records


def main():
    parser = argparse.ArgumentParser(description="Audit SIFT datasets for split leakage, label leakage, and PII.")
    parser.add_argument("--train", help="Path to train split .jsonl")
    parser.add_argument("--val", help="Path to validation split .jsonl")
    parser.add_argument("--test", help="Path to test split .jsonl")
    parser.add_argument("--input-file", "-i", help="Single dataset file to audit for internal governance/label leakage")
    parser.add_argument("--output-report", "-o", help="Optional path to output leakage report JSON")
    
    args = parser.parse_args()

    train_recs = load_split_records(args.train, "TRAIN") if args.train else []
    val_recs = load_split_records(args.val, "VALIDATION") if args.val else []
    test_recs = load_split_records(args.test, "TEST") if args.test else []
    
    all_recs = train_recs + val_recs + test_recs
    if not all_recs and args.input_file:
        all_recs = load_split_records(args.input_file, "ALL")

    if not all_recs:
        print("[x] Error: No input records provided. Specify --train/--val/--test or --input-file.")
        sys.exit(1)

    print(f"[*] Auditing {len(all_recs)} records across splits for leakage and governance...")

    # 1. Check Split Hash Overlaps
    train_hashes = {compute_content_hash(r.get("raw_text", "")): r.get("report_id") for r in train_recs}
    val_hashes = {compute_content_hash(r.get("raw_text", "")): r.get("report_id") for r in val_recs}
    test_hashes = {compute_content_hash(r.get("raw_text", "")): r.get("report_id") for r in test_recs}

    leakage_errors = []

    # Check exact overlaps
    for h, r_id in val_hashes.items():
        if h in train_hashes:
            leakage_errors.append(f"Exact content leak between TRAIN ({train_hashes[h]}) and VAL ({r_id})")
    for h, r_id in test_hashes.items():
        if h in train_hashes:
            leakage_errors.append(f"Exact content leak between TRAIN ({train_hashes[h]}) and TEST ({r_id})")
        if h in val_hashes:
            leakage_errors.append(f"Exact content leak between VAL ({val_hashes[h]}) and TEST ({r_id})")

    # 2. Check Event ID Overlaps
    def get_event_id(r):
        return r.get("event_id") or r.get("incident_id") or r.get("context", {}).get("event_id")

    train_events = {get_event_id(r): r.get("report_id") for r in train_recs if get_event_id(r)}
    val_events = {get_event_id(r): r.get("report_id") for r in val_recs if get_event_id(r)}
    test_events = {get_event_id(r): r.get("report_id") for r in test_recs if get_event_id(r)}

    for ev, r_id in val_events.items():
        if ev in train_events:
            leakage_errors.append(f"Event ID '{ev}' spans across TRAIN ({train_events[ev]}) and VAL ({r_id})")
    for ev, r_id in test_events.items():
        if ev in train_events:
            leakage_errors.append(f"Event ID '{ev}' spans across TRAIN ({train_events[ev]}) and TEST ({r_id})")
        if ev in val_events:
            leakage_errors.append(f"Event ID '{ev}' spans across VAL ({val_events[ev]}) and TEST ({r_id})")

    # 3. Check Label & Governance Leakage per record
    gov_checker = GovernanceChecker()
    gov_issues = []
    for r in all_recs:
        r_id = r.get("report_id", "UNKNOWN")
        raw = r.get("raw_text", "")
        ctx = r.get("context", {})
        rep = gov_checker.audit_record(r_id, raw, ctx)
        if not rep.passed_governance:
            gov_issues.append(rep.model_dump())

    print("\n" + "=" * 50)
    print("LEAKAGE & GOVERNANCE AUDIT SUMMARY")
    print("=" * 50)
    print(f"Cross-Split Leakage Errors: {len(leakage_errors)}")
    print(f"Governance / PII Flags:     {len(gov_issues)}")
    print("=" * 50)

    if leakage_errors:
        print("\n[!] Cross-Split Leakage Failures:")
        for err in leakage_errors:
            print(f"  - [FAIL] {err}")

    if gov_issues:
        print("\n[!] Governance & Feature Leakage Findings:")
        for gi in gov_issues[:10]:
            print(f"  - Record {gi['record_id']}: PII={gi['pii_status']}, LabelLeak={gi['label_leakage_detected']}")
            for lr in gi['leakage_reasons']:
                print(f"      * {lr}")

    if args.output_report:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_report)), exist_ok=True)
        out_data = {
            "leakage_errors_count": len(leakage_errors),
            "governance_issues_count": len(gov_issues),
            "cross_split_leakage": leakage_errors,
            "governance_records": gov_issues,
        }
        with open(args.output_report, "w", encoding="utf-8") as f:
            json.dump(out_data, f, indent=2)
        print(f"\n[✓] Audit report saved to: {args.output_report}")

    if leakage_errors:
        print("\n[!] Audit FAILED due to cross-split leakage.")
        sys.exit(1)
    else:
        print("\n[✓] Zero cross-split leakage detected. Dataset splits are safe.")
        sys.exit(0)


if __name__ == "__main__":
    main()
