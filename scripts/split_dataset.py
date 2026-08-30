#!/usr/bin/env python3
"""SIFT Dataset Splitting CLI.

Partitions validated dataset records into reproducible, temporal out-of-time splits
while preserving incident/event group integrity.

Usage:
    python scripts/split_dataset.py --input data/validated/dataset.jsonl --output-dir data/splits/ --version 1.0.0
"""

import argparse
import json
import os
import sys

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "api")))

from data_pipeline.splitting import DatasetSplitter, SplitConfig
from data_pipeline.duplicates import DuplicateDetector


def main():
    parser = argparse.ArgumentParser(description="Split validated SIFT records into Train, Validation, and Test sets.")
    parser.add_argument("--input", "-i", required=True, help="Path to input validated .jsonl file")
    parser.add_argument("--output-dir", "-o", required=True, help="Directory to write split files")
    parser.add_argument("--version", "-v", default="1.0.0", help="Dataset version (e.g. 1.0.0)")
    parser.add_argument("--train-ratio", type=float, default=0.70, help="Train split ratio (default: 0.70)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="Validation split ratio (default: 0.15)")
    parser.add_argument("--test-ratio", type=float, default=0.15, help="Test split ratio (default: 0.15)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic tie-breaking (default: 42)")
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[x] Error: Input file '{args.input}' not found.")
        sys.exit(1)

    records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"[*] Loaded {len(records)} records. Running cluster deduplication to prevent near-duplicate split leakage...")
    detector = DuplicateDetector(near_duplicate_threshold=0.85)
    dup_results, _ = detector.process_corpus(records)
    record_clusters = {r_id: res.cluster_id for r_id, res in dup_results.items()}

    config = SplitConfig(
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        random_seed=args.seed,
    )
    splitter = DatasetSplitter(config=config)
    split_res = splitter.split(records, record_clusters=record_clusters)

    os.makedirs(args.output_dir, exist_ok=True)
    prefix = f"sift_dataset_v{args.version}"

    train_path = os.path.join(args.output_dir, f"{prefix}_train.jsonl")
    val_path = os.path.join(args.output_dir, f"{prefix}_validation.jsonl")
    test_path = os.path.join(args.output_dir, f"{prefix}_test.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for r in split_res.train_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(val_path, "w", encoding="utf-8") as f:
        for r in split_res.val_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(test_path, "w", encoding="utf-8") as f:
        for r in split_res.test_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print("\n" + "=" * 50)
    print(f"DATASET SPLIT SUMMARY (v{args.version})")
    print("=" * 50)
    print(f"Train Records (70%):      {len(split_res.train_records)} -> {train_path}")
    print(f"Validation Records (15%): {len(split_res.val_records)} -> {val_path}")
    print(f"Test Records (15%):       {len(split_res.test_records)} -> {test_path}")
    print(f"High-SIF in Test:         {split_res.metrics.test_high_sif_count} ({split_res.metrics.high_sif_test_pct}%)")
    print(f"Leakage Check Passed:     {split_res.leakage_passed}")
    print("=" * 50)

    if split_res.metrics.warnings:
        print("\nWarnings:")
        for w in split_res.metrics.warnings:
            print(f"  [!] {w}")

    print(f"\n[✓] Successfully partitioned dataset into {args.output_dir}")


if __name__ == "__main__":
    main()
