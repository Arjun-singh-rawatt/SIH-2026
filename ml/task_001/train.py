#!/usr/bin/env python3
"""SIFT TASK-001 Training & Validation Pipeline CLI.

Orchestrates:
1. Loading & validating Train, Validation, and Test splits.
2. Fitting TF-IDF features on Training partition only.
3. Training Logistic Regression and Linear SVM candidate models.
4. Comparing candidate performance on the Validation split.
5. Selecting best baseline configuration.
6. Evaluating selected model once on out-of-time Test split.
7. Saving serialized joblib artifact, confusion matrix, and experiment lineage.

Usage:
    python -m ml.task_001.train --train data/splits/train.jsonl --val data/splits/val.jsonl --test data/splits/test.jsonl --dataset-version 1.0.0
"""

import argparse
from datetime import datetime, timezone
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api")))

from ml.common.dataset_loader import DatasetSplitLoader, LoadedDatasetSplit
from ml.common.metrics import compute_classification_metrics, generate_confusion_matrix_plot
from ml.common.errors import FalseNegativeAnalyzer
from ml.common.experiment import ExperimentTracker
from ml.task_001.features import TfidfFeatureExtractor, TfidfConfig
from ml.task_001.models import build_candidate_models, BaseSIFModel
from ml.task_001.inference import SIFClassifier


def train_task_001_baseline(
    train_path: str,
    val_path: Optional[str] = None,
    test_path: Optional[str] = None,
    dataset_version: str = "1.0.0",
    output_dir: str = "experiments/task_001",
    model_output_dir: str = "models/task_001",
    random_seed: int = 42,
    is_demo: bool = False,
) -> Tuple[SIFClassifier, Dict[str, Any]]:
    """Execute complete TASK-001 training, model selection, and evaluation pipeline."""
    exp_id = f"exp-task001-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    exp_dir = os.path.join(output_dir, exp_id)
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(model_output_dir, exist_ok=True)

    print("=" * 65)
    print(f" SIFT TASK-001: SIF POTENTIAL CLASSIFICATION BASELINE")
    print(f" Experiment ID: {exp_id} | Dataset Version: {dataset_version}")
    print("=" * 65)

    # 1. Load and Validate Dataset Splits
    print(f"\n[1/6] Ingesting and validating dataset splits...")
    train_split = DatasetSplitLoader.load_split(train_path, "TRAIN")
    print(f"      Train Samples:      {train_split.total_count} (High-SIF: {train_split.high_sif_count}, {train_split.high_sif_percentage}%)")
    print(f"      Class Distribution: {train_split.class_distribution}")

    val_split = None
    if val_path and os.path.exists(val_path):
        val_split = DatasetSplitLoader.load_split(val_path, "VALIDATION")
        print(f"      Validation Samples: {val_split.total_count} (High-SIF: {val_split.high_sif_count}, {val_split.high_sif_percentage}%)")

    test_split = None
    if test_path and os.path.exists(test_path):
        test_split = DatasetSplitLoader.load_split(test_path, "TEST")
        print(f"      Test Samples:       {test_split.total_count} (High-SIF: {test_split.high_sif_count}, {test_split.high_sif_percentage}%)")

    # 2. Fit TF-IDF on Train Data ONLY
    print(f"\n[2/6] Fitting TF-IDF feature extractor on TRAIN partition only (zero test leakage)...")
    tfidf_config = TfidfConfig(ngram_range=(1, 2), sublinear_tf=True, min_df=1)
    extractor = TfidfFeatureExtractor(config=tfidf_config)
    X_train = extractor.fit_transform_train(train_split.texts)
    print(f"      Learned Vocabulary Size: {extractor.vocabulary_size} word n-grams")

    # 3. Train Candidate Models
    print(f"\n[3/6] Training classical baseline candidate models...")
    candidates = build_candidate_models(random_seed=random_seed)
    for name, model in candidates.items():
        model.fit(X_train, train_split.labels)
        print(f"      Trained: {model.name}")

    # 4. Model Selection on Validation Split
    print(f"\n[4/6] Evaluating candidate models on VALIDATION split...")
    eval_target_split = val_split if (val_split and val_split.total_count > 0) else train_split
    X_eval = extractor.transform(eval_target_split.texts)
    
    candidate_results: Dict[str, Any] = {}
    best_candidate_name = None
    best_candidate_f1 = -1.0
    best_candidate_high_sif = -1.0

    print("\n" + "-" * 65)
    print(f"{'Candidate Model':<30} | {'Accuracy':<8} | {'Macro F1':<8} | {'High-SIF Rec':<12}")
    print("-" * 65)

    for name, model in candidates.items():
        y_pred = model.predict(X_eval)
        m = compute_classification_metrics(eval_target_split.labels, y_pred)
        candidate_results[name] = m
        print(f"{name:<30} | {m.accuracy:<8.2%} | {m.macro_f1:<8.4f} | {m.high_sif_recall:<12.2%}")

        # Model selection heuristic: Prioritize Macro F1 and High-SIF Recall
        score = m.macro_f1 * 0.5 + m.high_sif_recall * 0.5
        if score > (best_candidate_f1 * 0.5 + best_candidate_high_sif * 0.5):
            best_candidate_f1 = m.macro_f1
            best_candidate_high_sif = m.high_sif_recall
            best_candidate_name = name

    print("-" * 65)
    print(f"[✓] Selected Winning Baseline: {best_candidate_name}")
    winning_model = candidates[best_candidate_name]

    # 5. Final Out-of-Time Test Evaluation
    print(f"\n[5/6] Evaluating winning baseline ONCE on out-of-time TEST split...")
    test_metrics = None
    error_report = None
    predictions_payload = []

    if test_split and test_split.total_count > 0:
        X_test = extractor.transform(test_split.texts)
        y_test_pred = winning_model.predict(X_test)
        scores_list, score_type = winning_model.predict_scores(X_test)
        
        test_metrics = compute_classification_metrics(test_split.labels, y_test_pred)
        error_report = FalseNegativeAnalyzer.analyze(
            report_ids=test_split.report_ids,
            texts=test_split.texts,
            y_true=test_split.labels,
            y_pred=y_test_pred,
            decision_scores=scores_list,
        )

        for r_id, raw, y_t, y_p, sc in zip(test_split.report_ids, test_split.texts, test_split.labels, y_test_pred, scores_list):
            predictions_payload.append({
                "report_id": r_id,
                "raw_text_excerpt": (raw[:100] + "...") if len(raw) > 100 else raw,
                "actual_label": y_t,
                "predicted_label": y_p,
                "scores": sc,
            })

        print(f"      Test Accuracy:        {test_metrics.accuracy:.2%}")
        print(f"      Test Macro F1:        {test_metrics.macro_f1:.4f}")
        print(f"      Test High-SIF Recall: {test_metrics.high_sif_recall:.2%} ({test_metrics.high_sif_correct}/{test_metrics.high_sif_support})")
        print(f"      High-SIF False Negs:  {error_report.total_high_sif_false_negatives}")

        # Render Confusion Matrix Plot
        cm_plot_path = os.path.join(exp_dir, "confusion_matrix.png")
        generate_confusion_matrix_plot(
            test_metrics,
            output_path=cm_plot_path,
            title=f"SIFT TASK-001 Baseline Confusion Matrix ({best_candidate_name})",
        )
        print(f"      Confusion Matrix Plot: {cm_plot_path}")

    # 6. Save Artifacts & Experiment Lineage
    print(f"\n[6/6] Packaging model artifact and experiment lineage...")
    model_version = f"sift-task-001-baseline-v{dataset_version}"
    classifier = SIFClassifier(
        extractor=extractor,
        model=winning_model,
        model_version=model_version,
        taxonomy_version="1.0",
        metadata={
            "experiment_id": exp_id,
            "dataset_version": dataset_version,
            "is_demo": is_demo,
            "best_candidate": best_candidate_name,
            "trained_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    artifact_filename = f"{model_version}.joblib"
    artifact_path = os.path.join(model_output_dir, artifact_filename)
    classifier.save(artifact_path)
    print(f"      Model Artifact Saved: {artifact_path}")

    run_record = ExperimentTracker.create_run_record(
        experiment_id=exp_id,
        task="TASK-001",
        dataset_version=dataset_version,
        model_type=winning_model.name,
        feature_type=f"TF-IDF (ngram={tfidf_config.ngram_range}, sublinear_tf={tfidf_config.sublinear_tf})",
        hyperparameters=winning_model.get_params(),
        random_seed=random_seed,
        is_demo=is_demo,
    )
    run_record.model_artifact_path = artifact_path

    val_m = candidate_results.get(best_candidate_name)
    ExperimentTracker.save_experiment_bundle(
        run=run_record,
        output_dir=exp_dir,
        val_metrics=val_m,
        test_metrics=test_metrics,
        error_report=error_report,
        predictions=predictions_payload,
    )
    print(f"      Experiment Bundle:    {exp_dir}")

    print("\n" + "=" * 65)
    print(f" [✓] BASELINE TRAINING COMPLETE: {best_candidate_name}")
    print("=" * 65)

    return classifier, {
        "experiment_id": exp_id,
        "model_artifact": artifact_path,
        "experiment_dir": exp_dir,
        "val_metrics": val_m.model_dump() if val_m else None,
        "test_metrics": test_metrics.model_dump() if test_metrics else None,
    }


def main():
    parser = argparse.ArgumentParser(description="Train SIFT TASK-001 SIF Potential classification baseline.")
    parser.add_argument("--train", "-t", required=True, help="Path to train split JSONL")
    parser.add_argument("--val", "--validation", "-v", help="Path to validation split JSONL")
    parser.add_argument("--test", help="Path to test split JSONL")
    parser.add_argument("--dataset-version", default="0.1.0", help="Dataset version string (default: 0.1.0)")
    parser.add_argument("--output-dir", "-o", default="experiments/task_001", help="Experiment outputs directory")
    parser.add_argument("--model-output", "-m", default="models/task_001", help="Model artifact destination directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--demo", action="store_true", help="Flag indicating training on synthetic demo data")

    args = parser.parse_args()

    train_task_001_baseline(
        train_path=args.train,
        val_path=args.val,
        test_path=args.test,
        dataset_version=args.dataset_version,
        output_dir=args.output_dir,
        model_output_dir=args.model_output,
        random_seed=args.seed,
        is_demo=args.demo,
    )


if __name__ == "__main__":
    main()
