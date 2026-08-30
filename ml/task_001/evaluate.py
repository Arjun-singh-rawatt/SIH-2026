#!/usr/bin/env python3
"""SIFT TASK-001 Standalone Evaluation CLI.

Evaluates a saved .joblib model artifact against any test split without retraining.

Usage:
    python -m ml.task_001.evaluate --model models/task_001/sift-task-001-baseline-v0.1.0.joblib --test data/splits/test.jsonl
"""

import argparse
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
from ml.task_001.inference import SIFClassifier


def evaluate_model(model_path: str, test_path: str, output_dir: Optional[str] = None):
    print(f"[*] Loading model artifact from: {model_path}")
    classifier = SIFClassifier.load(model_path)
    print(f"    Loaded Model Version: {classifier.model_version} ({classifier.model.name})")

    print(f"[*] Loading test split from: {test_path}")
    test_split = DatasetSplitLoader.load_split(test_path, "TEST")
    print(f"    Total Test Samples: {test_split.total_count}")

    # Predict
    preds = classifier.predict_batch(test_split.texts)
    y_pred = [p.predicted_sif_potential for p in preds]
    scores_list = [p.decision_scores.scores for p in preds]

    # Metrics
    metrics = compute_classification_metrics(test_split.labels, y_pred)
    error_report = FalseNegativeAnalyzer.analyze(
        report_ids=test_split.report_ids,
        texts=test_split.texts,
        y_true=test_split.labels,
        y_pred=y_pred,
        decision_scores=scores_list,
    )

    print("\n" + "=" * 60)
    print(f"STANDALONE EVALUATION RESULTS: {classifier.model_version}")
    print("=" * 60)
    print(f"Overall Accuracy:        {metrics.accuracy:.2%}")
    print(f"Macro F1 Score:          {metrics.macro_f1:.4f}")
    print(f"Weighted F1 Score:       {metrics.weighted_f1:.4f}")
    print(f"Safety High-SIF Recall:  {metrics.high_sif_recall:.2%} ({metrics.high_sif_correct}/{metrics.high_sif_support})")
    print(f"High-SIF False Negatives:{error_report.total_high_sif_false_negatives}")
    print("-" * 60)

    print(f"{'SIF Class':<15} | {'Support':<8} | {'Precision':<10} | {'Recall':<10} | {'F1 Score':<10}")
    print("-" * 60)
    for c in metrics.per_class_metrics:
        print(f"{c.class_name:<15} | {c.support:<8} | {c.precision:<10.4f} | {c.recall:<10.4f} | {c.f1_score:<10.4f}")
    print("=" * 60)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        metrics_file = os.path.join(output_dir, "eval_metrics.json")
        with open(metrics_file, "w", encoding="utf-8") as f:
            f.write(metrics.model_dump_json(indent=2))

        cm_plot = os.path.join(output_dir, "eval_confusion_matrix.png")
        generate_confusion_matrix_plot(metrics, cm_plot, title="SIFT Evaluation Confusion Matrix")
        print(f"\n[✓] Evaluation artifacts written to: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate a saved SIFT model artifact on test data.")
    parser.add_argument("--model", "-m", required=True, help="Path to .joblib model artifact")
    parser.add_argument("--test", "-t", required=True, help="Path to test split .jsonl")
    parser.add_argument("--output-dir", "-o", help="Optional output directory for reports")

    args = parser.parse_args()
    evaluate_model(args.model, args.test, args.output_dir)


if __name__ == "__main__":
    main()
