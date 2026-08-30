#!/usr/bin/env python3
"""SIFT Dataset Ingestion CLI.

Parses raw data files (JSON, JSONL, CSV) and writes canonical interim JSONL records.

Usage:
    python scripts/ingest_dataset.py --input data/raw/source.csv --output data/interim/normalized.jsonl
"""

import argparse
import json
import os
import sys

# Ensure root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from data_pipeline.ingestion import DataIngester
from data_pipeline.normalization import normalize_text


def main():
    parser = argparse.ArgumentParser(description="Ingest raw safety report data into SIFT canonical format.")
    parser.add_argument("--input", "-i", required=True, help="Path to input raw file (.json, .jsonl, .csv)")
    parser.add_argument("--output", "-o", required=True, help="Path to output interim .jsonl file")
    parser.add_argument("--normalize", action="store_true", default=True, help="Apply deterministic text normalization")
    
    args = parser.parse_args()

    print(f"[*] Ingesting raw data from: {args.input}")
    ingester = DataIngester()
    records = ingester.ingest_file(args.input)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    eligible_count = 0
    ineligible_count = 0

    with open(args.output, "w", encoding="utf-8") as f:
        for rec in records:
            if rec.is_eligible:
                data = rec.raw_data
                if args.normalize and "raw_text" in data:
                    data["raw_text"] = normalize_text(data["raw_text"])
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
                eligible_count += 1
            else:
                ineligible_count += 1
                print(f"[!] Skipped ineligible record {rec.source_record_id}: {rec.ineligibility_reason}")

    print(f"[✓] Successfully ingested {eligible_count} records (skipped {ineligible_count} ineligible).")
    print(f"[✓] Output written to: {args.output}")


if __name__ == "__main__":
    main()
