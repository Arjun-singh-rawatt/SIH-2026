#!/usr/bin/env python3
"""SIFT Dataset Validation CLI.

Audits dataset files against canonical Pydantic schemas, taxonomy enumerations,
exact evidence span offsets, and annotation lifecycle states.

Usage:
    python scripts/validate_dataset.py --input data/validated/dataset.jsonl
"""

import argparse
import json
import os
import sys

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from data_pipeline.validation import DatasetValidator, ValidationSeverity


def main():
    parser = argparse.ArgumentParser(description="Validate SIFT dataset files against canonical specifications.")
    parser.add_argument("--input", "-i", required=True, help="Path to .jsonl dataset file")
    parser.add_argument("--strict", action="store_true", default=True, help="Enforce strict taxonomy matching")
    parser.add_argument("--output-report", "-r", help="Optional path to output validation report JSON")
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[x] Error: Input file '{args.input}' not found.")
        sys.exit(1)

    validator = DatasetValidator(strict_taxonomy=args.strict)
    
    valid_count = 0
    invalid_count = 0
    warning_count = 0
    reports = []

    print(f"[*] Validating records in: {args.input}")

    with open(args.input, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except Exception as e:
                print(f"[x] Line {line_no}: JSON parse error - {e}")
                invalid_count += 1
                continue

            res = validator.validate_record_dict(data)
            reports.append(res.to_dict())

            if res.is_valid:
                valid_count += 1
                if res.has_warnings:
                    warning_count += 1
                    for w in res.warnings:
                        print(f"  [WARN] {res.record_id} -> {w.field}: {w.message}")
            else:
                invalid_count += 1
                print(f"  [FAIL] {res.record_id} failed validation:")
                for err in res.errors:
                    print(f"    - {err.field}: {err.message}")

    print("\n" + "=" * 50)
    print("VALIDATION SUMMARY")
    print("=" * 50)
    print(f"Total Records Inspected: {valid_count + invalid_count}")
    print(f"Valid Records:           {valid_count}")
    print(f"Invalid Records:         {invalid_count}")
    print(f"Records with Warnings:   {warning_count}")
    print("=" * 50)

    if args.output_report:
        os.makedirs(os.path.dirname(os.path.abspath(args.output_report)), exist_ok=True)
        summary = {
            "input_file": args.input,
            "total": valid_count + invalid_count,
            "valid": valid_count,
            "invalid": invalid_count,
            "with_warnings": warning_count,
            "details": reports,
        }
        with open(args.output_report, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)
        print(f"[✓] Detailed report saved to: {args.output_report}")

    if invalid_count > 0:
        print("[!] Validation failed with critical errors.")
        sys.exit(1)
    else:
        print("[✓] All inspected records passed validation successfully.")
        sys.exit(0)


if __name__ == "__main__":
    main()
