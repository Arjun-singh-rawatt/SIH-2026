#!/usr/bin/env python3
"""SIFT TASK-001 Standalone Transformer Evaluation CLI.

Loads a saved transformer model checkpoint and tokenizer from disk and evaluates
it against a specified dataset split without any retraining.

Usage:
    python -m ml.task_001_transformer.evaluate \
        --model-dir models/task_001/transformer/sift-task-001-transformer-v0.1.0 \
        --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl \
        --output-dir experiments/task_001/eval_run
"""

import argparse
from datetime import datetime, timezone
import json
import os
import sys
from typing import Optional

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api")))

from ml.common.dataset_loader import DatasetSplitLoader
from ml.common.metrics import compute_classification_metrics, generate_confusion_matrix_plot
from ml.common.errors import FalseNegativeAnalyzer
from ml.task_001_transformer.inference import SIFTransformerClassifier


def evaluate_task_001_transformer(
    model_dir: str,
    test_path: str,
    output_dir: Optional[str] = None,
    device: str = "auto",
    batch_size: int = 16,
):
    """Execute standalone evaluation of saved transformer artifact."""
    print("=" * 65)
    print(" SIFT TASK-001: STANDALONE TRANSFORMER EVALUATION")
    print(f" Model Directory: {model_dir}")
    print(f" Dataset Split:   {test_path}")
    print("=" * 65)

    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Model directory does not exist: {model_dir}")
    if not os.path.exists(test_path):
        raise FileNotFoundError(f"Test split file does not exist: {test_path}")

    # Load model wrapper
    print("\n[1/3] Loading saved transformer and tokenizer...")
    classifier = SIFTransformerClassifier.load(model_dir, device=device)
    print(f"      Loaded Model Version: {classifier.model_version}")
    print(f"      Compute Device:       {classifier.device}")

    # Load dataset split
    print("\n[2/3] Ingesting and validating target evaluation split...")
    split = DatasetSplitLoader.load_split(test_path, "EVALUATION")
    print(f"      Total Samples:        {split.total_count}")
    print(f"      High-SIF Support:     {split.high_sif_count} ({split.high_sif_percentage}%)")
    print(f"      Class Distribution:   {split.class_distribution}")

    # Run batch inference
    print("\n[3/3] Running inference and auditing metrics...")
    predictions = classifier.predict_batch(split.texts, batch_size=batch_size)
    pred_labels = [p.predicted_sif_potential for p in predictions]
    decision_scores = [p.decision_scores.scores for p in predictions]

    metrics = compute_classification_metrics(split.labels, pred_labels)
    error_report = FalseNegativeAnalyzer.analyze(
        report_ids=split.report_ids,
        texts=split.texts,
        y_true=split.labels,
        y_pred=pred_labels,
        decision_scores=decision_scores,
    )

    print("\n" + "-" * 65)
    print(f"{'Evaluation Metric':<30} | {'Value':<15} | {'Safety Specification'}")
    print("-" * 65)
    print(f"{'High-SIF Recall':<30} | {metrics.high_sif_recall:<15.2%} | >= 95.0%")
    print(f"{'Macro F1 Score':<30} | {metrics.macro_f1:<15.4f} | >= 0.8800")
    print(f"{'Accuracy':<30} | {metrics.accuracy:<15.2%} | Diagnostic")
    print(f"{'Weighted F1 Score':<30} | {metrics.weighted_f1:<15.4f} | Diagnostic")
    print(f"{'High-SIF False Negatives':<30} | {error_report.total_high_sif_false_negatives:<15} | Zero Tolerated")
    print("-" * 65)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        # Save metrics.json
        with open(os.path.join(output_dir, "metrics.json"), "w", encoding="utf-8") as f:
            f.write(metrics.model_dump_json(indent=2))

        # Save false_negatives.json
        with open(os.path.join(output_dir, "false_negatives.json"), "w", encoding="utf-8") as f:
            f.write(error_report.model_dump_json(indent=2))

        # Generate confusion matrix plot
        cm_path = os.path.join(output_dir, "confusion_matrix.png")
        generate_confusion_matrix_plot(
            metrics,
            output_path=cm_path,
            title=f"SIFT Transformer Evaluation ({classifier.model_version})",
        )
        print(f"\n[✓] Evaluation artifacts written to: {output_dir}")

    return metrics, error_report


def main():
    parser = argparse.ArgumentParser(description="Evaluate a saved SIFT transformer classifier.")
    parser.add_argument("--model-dir", "-m", required=True, help="Directory containing fine-tuned model and tokenizer")
    parser.add_argument("--test", "-t", required=True, help="Path to evaluation JSONL split")
    parser.add_argument("--output-dir", "-o", help="Optional output directory for metrics and confusion matrix")
    parser.add_argument("--device", default="auto", help="Compute device: auto, cpu, cuda, mps")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for evaluation")

    args = parser.parse_args()
    evaluate_task_001_transformer(
        model_dir=args.model_dir,
        test_path=args.test,
        output_dir=args.output_dir,
        device=args.device,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
