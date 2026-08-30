#!/usr/bin/env python3
"""SIFT Duplicate & Near-Duplicate Detection CLI.

Computes exact SHA-256 text hashes and pairwise Jaccard n-gram similarities to identify
potential duplicates, templated observations, and near-duplicate leakage clusters.

Usage:
    python scripts/detect_duplicates.py --input data/interim/normalized.jsonl --threshold 0.85
"""

import argparse
import json
import os
import sys

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from data_pipeline.duplicates import DuplicateDetector, DuplicateType


def main():
    parser = argparse.ArgumentParser(description="Detect exact and near duplicates in a SIFT dataset.")
    parser.add_argument("--input", "-i", required=True, help="Path to input .jsonl dataset file")
    parser.add_argument("--threshold", "-t", type=float, default=0.85, help="Jaccard similarity threshold for near duplicates (default: 0.85)")
    parser.add_argument("--output-report", "-o", help="Optional path to output JSON duplicate report")
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[x] Error: Input file '{args.input}' not found.")
        sys.exit(1)

    records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"[*] Analyzing {len(records)} records for exact and near duplicates (threshold: {args.threshold:.0%})...")
    detector = DuplicateDetector(near_duplicate_threshold=args.threshold)
    results, matches = detector.process_corpus(records)

    exact_dups = [r for r in results.values() if r.duplicate_type == DuplicateType.EXACT_DUPLICATE]
    near_dups = [r for r in results.values() if r.duplicate_type == DuplicateType.NEAR_DUPLICATE]
    uniques = [r for r in results.values() if r.duplicate_type == DuplicateType.UNIQUE]

    print("\n" + "=" * 50)
    print("DUPLICATE DETECTION RESULTS")
    print("=" * 50)
    print(f"Total Records Analyzed:    {len(records)}")
    print(f"Unique Records:            {len(uniques)}")
    print(f"Exact Duplicates (SHA256): {len(exact_dups)}")
    print(f"Near-Duplicates:           {len(near_dups)}")
    print(f"Pairwise Match Pairs:      {len(matches)}")
    print("=" * 50)

    if exact_dups:
        print("\n[!] Exact Duplicates Found:")
        for ed in exact_dups:
            print(f"  - Record {ed.record_id} is exact duplicate of {ed.exact_duplicate_of} (Hash: {ed.content_hash[:12]}...)")

    if matches:
        print("\n[!] Near-Duplicate Matches Found:")
        for m in matches[:10]:
            print(f"  - {m.record_id_a} <-> {m.record_id_b} (Similarity: {m.similarity_score:.1%}): {m.reason}")
        if len(matches) > 10:
            print(f"  ... and {len(matches) - 10} more matches.")

    if args.output_report:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_report)), exist_ok=True)
        report_data = {
            "total_records": len(records),
            "unique_count": len(uniques),
            "exact_duplicate_count": len(exact_dups),
            "near_duplicate_count": len(near_dups),
            "threshold": args.threshold,
            "record_classifications": {k: v.model_dump() for k, v in results.items()},
            "near_duplicate_matches": [m.model_dump() for m in matches],
        }
        with open(args.output_report, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"\n[✓] Detailed duplicate report saved to: {args.output_report}")


if __name__ == "__main__":
    main()
