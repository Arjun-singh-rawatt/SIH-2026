#!/usr/bin/env python3
"""SIFT TASK-001 Transformer Training & Validation Pipeline CLI.

Orchestrates:
1. Ingesting & validating Train, Validation, and Test splits.
2. Auditing narrative report length distribution to prevent evidence truncation.
3. Tokenizing safety observations with attention mask enforcement.
4. Computing training-partition class weights for loss balancing.
5. Training pretrained transformer encoder with sequence classification head.
6. Validation-based model checkpoint selection (prioritizing High-SIF Recall + Macro F1).
7. Single-pass out-of-time evaluation on locked Test partition.
8. Generating experiment lineage, false-negative diagnostics, confusion matrix, and baseline comparison.

Usage:
    python -m ml.task_001_transformer.train --train data/splits/sift_demo_dataset_v0.1.0_train.jsonl \
        --test data/splits/sift_demo_dataset_v0.1.0_test.jsonl --dataset-version 0.1.0 --demo
"""

import argparse
from datetime import datetime, timezone
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import torch
import transformers
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api")))

from ml.common.dataset_loader import DatasetSplitLoader, LoadedDatasetSplit
from ml.common.metrics import (
    compute_classification_metrics,
    generate_confusion_matrix_plot,
    CANONICAL_SIF_CLASSES,
)
from ml.common.errors import FalseNegativeAnalyzer
from ml.common.experiment import ExperimentTracker, ExperimentRun
from ml.task_001_transformer.config import (
    TransformerModelConfig,
    TrainingConfig,
    detect_compute_device,
    DEFAULT_LABEL2ID,
    DEFAULT_ID2LABEL,
)
from ml.task_001_transformer.tokenizer import SafetyReportTokenizer
from ml.task_001_transformer.dataset import SIFTextDataset, compute_class_weights
from ml.task_001_transformer.model import SIFTransformerModel
from ml.task_001_transformer.inference import SIFTransformerClassifier
from ml.task_001_transformer.comparison import (
    generate_comparative_report,
    format_comparative_markdown,
)


def set_reproducible_seed(seed: int):
    """Seed all pseudo-random generators for reproducible training runs."""
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def train_task_001_transformer(
    train_path: str,
    val_path: Optional[str] = None,
    test_path: Optional[str] = None,
    base_model: str = "distilbert-base-uncased",
    dataset_version: str = "0.1.0",
    output_dir: str = "experiments/task_001",
    model_output_dir: str = "models/task_001/transformer",
    epochs: int = 3,
    batch_size: int = 8,
    learning_rate: float = 2e-5,
    max_length: int = 128,
    weight_decay: float = 0.01,
    warmup_ratio: float = 0.1,
    random_seed: int = 42,
    device: str = "auto",
    use_class_weights: bool = True,
    smoke_test: bool = False,
    is_demo: bool = False,
    classical_model_path: Optional[str] = None,
) -> Tuple[SIFTransformerClassifier, Dict[str, Any]]:
    """Execute complete TASK-001 Transformer training, checkpoint selection, and evaluation."""
    set_reproducible_seed(random_seed)
    compute_dev = detect_compute_device(device)

    exp_id = f"exp-task001-transformer-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    exp_dir = os.path.join(output_dir, exp_id)
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(model_output_dir, exist_ok=True)

    print("=" * 70)
    print(" SIFT TASK-001: PRETRAINED TRANSFORMER BENCHMARK")
    print(f" Experiment ID: {exp_id} | Dataset Version: {dataset_version}")
    print(f" Base Model:    {base_model} | Compute Device: {compute_dev}")
    print(f" Execution Mode: {'SMOKE-TEST' if smoke_test else ('DEMO / PIPELINE TEST' if is_demo else 'PRODUCTION RUN')}")
    print("=" * 70)

    # 1. Ingest and Validate Dataset Splits
    print("\n[1/7] Ingesting and validating dataset splits...")
    train_split = DatasetSplitLoader.load_split(train_path, "TRAIN")
    print(f"      Train Samples:      {train_split.total_count} (High-SIF: {train_split.high_sif_count}, {train_split.high_sif_percentage}%)")
    print(f"      Class Distribution: {train_split.class_distribution}")

    val_split = None
    if val_path and os.path.exists(val_path):
        val_candidate = DatasetSplitLoader.load_split(val_path, "VALIDATION")
        if val_candidate.total_count > 0:
            val_split = val_candidate
            print(f"      Validation Samples: {val_split.total_count} (High-SIF: {val_split.high_sif_count}, {val_split.high_sif_percentage}%)")
        else:
            print("      Validation Split:   Empty (0 records). Using train split for diagnostic checkpointing.")

    test_split = None
    if test_path and os.path.exists(test_path):
        test_split = DatasetSplitLoader.load_split(test_path, "TEST")
        print(f"      Test Samples:       {test_split.total_count} (High-SIF: {test_split.high_sif_count}, {test_split.high_sif_percentage}%)")
        print("      [LOCKED TEST SET PROTECTED: Evaluated strictly once after model selection]")

    # 2. Tokenizer & Report Length Audit
    print("\n[2/7] Initializing tokenizer & auditing safety narrative length distributions...")
    tokenizer = SafetyReportTokenizer(model_name_or_path=base_model, max_length=max_length)
    all_narratives = list(train_split.texts)
    if val_split:
        all_narratives.extend(val_split.texts)
    if test_split:
        all_narratives.extend(test_split.texts)

    length_audit = tokenizer.analyze_length_distribution(all_narratives, max_length=max_length)
    print(f"      Configured Max Sequence Length: {max_length}")
    print(f"      Token Lengths -> Min: {length_audit['token_distribution']['min']}, "
          f"Median: {length_audit['token_distribution']['median']}, "
          f"P95: {length_audit['token_distribution']['p95']}, "
          f"Max: {length_audit['token_distribution']['max']}")
    print(f"      Truncated Observations: {length_audit['truncated_reports_count']} ({length_audit['truncated_percentage']}%)")

    # 3. Class Imbalance & Loss Weight Calculation
    print("\n[3/7] Analyzing class distribution and computing loss weights...")
    class_weights_tensor = None
    if use_class_weights:
        class_weights_tensor = compute_class_weights(
            labels=train_split.labels,
            label2id=DEFAULT_LABEL2ID,
            num_classes=len(CANONICAL_SIF_CLASSES),
        )
        print("      Class-Weighted Cross-Entropy enabled:")
        for cls_name, cls_idx in DEFAULT_LABEL2ID.items():
            print(f"        - {cls_name:<10}: {class_weights_tensor[cls_idx]:.3f}")
    else:
        print("      Standard Cross-Entropy enabled (no class weighting).")

    # 4. Model & Optimizer Initialization
    print(f"\n[4/7] Initializing pretrained transformer encoder: {base_model}...")
    model_cfg = TransformerModelConfig(
        base_model=base_model,
        num_labels=len(CANONICAL_SIF_CLASSES),
        max_length=max_length,
        label2id=DEFAULT_LABEL2ID,
        id2label=DEFAULT_ID2LABEL,
    )
    sif_model = SIFTransformerModel(
        config=model_cfg,
        class_weights=class_weights_tensor,
    )
    sif_model.to(compute_dev)

    print(f"      Total Parameters:     {sif_model.num_parameters:,}")
    print(f"      Trainable Parameters: {sif_model.trainable_parameters:,}")

    # Prepare DataLoaders
    train_dataset = SIFTextDataset(
        texts=train_split.texts,
        labels=train_split.labels,
        report_ids=train_split.report_ids,
        tokenizer=tokenizer,
        max_length=max_length,
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=min(batch_size, len(train_dataset)),
        shuffle=True,
    )

    eval_split_target = val_split if (val_split and val_split.total_count > 0) else train_split
    val_dataset = SIFTextDataset(
        texts=eval_split_target.texts,
        labels=eval_split_target.labels,
        report_ids=eval_split_target.report_ids,
        tokenizer=tokenizer,
        max_length=max_length,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=min(batch_size, len(val_dataset)),
        shuffle=False,
    )

    # Optimizer and Linear Warmup Scheduler
    effective_epochs = 1 if smoke_test else epochs
    optimizer = torch.optim.AdamW(
        sif_model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
    )
    total_steps = len(train_loader) * effective_epochs
    warmup_steps = int(total_steps * warmup_ratio)
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=max(1, total_steps),
    )

    # 5. Training Loop with Validation-Based Checkpoint Selection
    print(f"\n[5/7] Executing training loop ({effective_epochs} epoch{'s' if effective_epochs > 1 else ''})...")
    best_score = -1.0
    best_val_metrics = None
    best_state_dict = None

    print("-" * 70)
    print(f"{'Epoch':<8} | {'Train Loss':<12} | {'Val Acc':<10} | {'Val Macro F1':<14} | {'Val High-SIF Rec':<16}")
    print("-" * 70)

    for epoch in range(1, effective_epochs + 1):
        sif_model.train()
        total_train_loss = 0.0

        for batch in train_loader:
            optimizer.zero_grad()
            input_ids = batch["input_ids"].to(compute_dev)
            attention_mask = batch["attention_mask"].to(compute_dev)
            labels = batch["label"].to(compute_dev)

            outputs = sif_model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs["loss"]
            loss.backward()
            torch.nn.utils.clip_grad_norm_(sif_model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()
            total_train_loss += float(loss.item())

        avg_train_loss = total_train_loss / max(1, len(train_loader))

        # Evaluate on validation split for model selection
        sif_model.eval()
        val_preds: List[str] = []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(compute_dev)
                attention_mask = batch["attention_mask"].to(compute_dev)
                outputs = sif_model(input_ids=input_ids, attention_mask=attention_mask)
                pred_indices = outputs["probabilities"].argmax(dim=-1).cpu().numpy()
                for idx in pred_indices:
                    val_preds.append(DEFAULT_ID2LABEL[int(idx)])

        epoch_val_metrics = compute_classification_metrics(eval_split_target.labels, val_preds)

        # Selection policy: 0.6 * High-SIF Recall + 0.4 * Macro F1
        selection_score = (epoch_val_metrics.high_sif_recall * 0.6) + (epoch_val_metrics.macro_f1 * 0.4)

        print(
            f"{epoch:<8} | {avg_train_loss:<12.4f} | {epoch_val_metrics.accuracy:<10.2%} | "
            f"{epoch_val_metrics.macro_f1:<14.4f} | {epoch_val_metrics.high_sif_recall:<16.2%}"
        )

        if selection_score >= best_score:
            best_score = selection_score
            best_val_metrics = epoch_val_metrics
            best_state_dict = {k: v.cpu().clone() for k, v in sif_model.state_dict().items()}

    print("-" * 70)
    print(f"[✓] Checkpoint Selected (Validation Score: {best_score:.4f})")

    # Restore best checkpoint
    if best_state_dict is not None:
        sif_model.load_state_dict(best_state_dict)
        sif_model.to(compute_dev)

    # 6. Final Out-of-Time Test Evaluation (Evaluated Strictly ONCE)
    print("\n[6/7] Evaluating selected checkpoint ONCE on locked out-of-time TEST split...")
    test_metrics = None
    error_report = None
    predictions_payload = []
    y_test_pred: List[str] = []
    comparative_report = None

    if test_split and test_split.total_count > 0:
        sif_model.eval()
        test_dataset = SIFTextDataset(
            texts=test_split.texts,
            labels=test_split.labels,
            report_ids=test_split.report_ids,
            tokenizer=tokenizer,
            max_length=max_length,
        )
        test_loader = DataLoader(test_dataset, batch_size=len(test_dataset), shuffle=False)

        test_scores_list: List[Dict[str, float]] = []
        with torch.no_grad():
            for batch in test_loader:
                input_ids = batch["input_ids"].to(compute_dev)
                attention_mask = batch["attention_mask"].to(compute_dev)
                outputs = sif_model(input_ids=input_ids, attention_mask=attention_mask)
                probs = outputs["probabilities"].cpu().numpy()

                for prob_vec in probs:
                    pred_idx = int(prob_vec.argmax())
                    pred_label = DEFAULT_ID2LABEL[pred_idx]
                    y_test_pred.append(pred_label)

                    scores_dict = {
                        DEFAULT_ID2LABEL[idx]: round(float(prob_vec[idx]), 4)
                        for idx in range(len(prob_vec))
                    }
                    test_scores_list.append(scores_dict)

        test_metrics = compute_classification_metrics(test_split.labels, y_test_pred)
        error_report = FalseNegativeAnalyzer.analyze(
            report_ids=test_split.report_ids,
            texts=test_split.texts,
            y_true=test_split.labels,
            y_pred=y_test_pred,
            decision_scores=test_scores_list,
        )

        for r_id, raw, y_t, y_p, sc in zip(
            test_split.report_ids, test_split.texts, test_split.labels, y_test_pred, test_scores_list
        ):
            predictions_payload.append({
                "report_id": r_id,
                "raw_text_excerpt": (raw[:100] + "...") if len(raw) > 100 else raw,
                "actual_label": y_t,
                "predicted_label": y_p,
                "probabilities": sc,
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
            title=f"SIFT TASK-001 Transformer Confusion Matrix ({base_model})",
        )
        print(f"      Confusion Matrix Plot: {cm_plot_path}")

        # Comparative Baseline Benchmark
        default_baseline = (
            "models/task_001/baseline/sift-task-001-baseline-v0.1.0.joblib"
            if os.path.exists("models/task_001/baseline/sift-task-001-baseline-v0.1.0.joblib")
            else "models/task_001/sift-task-001-baseline-v0.1.0.joblib"
        )
        classical_model_file = classical_model_path or default_baseline
        if os.path.exists(classical_model_file):
            print(f"\n      Comparing against classical baseline: {classical_model_file}")
            try:
                from ml.task_001.inference import SIFClassifier
                classical_clf = SIFClassifier.load(classical_model_file)
                classical_preds_objs = classical_clf.predict_batch(test_split.texts)
                classical_preds = [p.predicted_sif_potential for p in classical_preds_objs]
                classical_metrics = compute_classification_metrics(test_split.labels, classical_preds)

                comparative_report = generate_comparative_report(
                    report_ids=test_split.report_ids,
                    texts=test_split.texts,
                    y_true=test_split.labels,
                    y_classical_pred=classical_preds,
                    y_transformer_pred=y_test_pred,
                    classical_metrics=classical_metrics.model_dump(),
                    transformer_metrics=test_metrics.model_dump(),
                    classical_model_name=classical_clf.model.name,
                    transformer_model_name=base_model,
                    dataset_version=dataset_version,
                    is_demo=is_demo,
                )

                # Save comparative report
                comp_json = os.path.join(exp_dir, "comparison_with_baseline.json")
                with open(comp_json, "w", encoding="utf-8") as f:
                    f.write(comparative_report.model_dump_json(indent=2))

                comp_md = os.path.join(exp_dir, "comparison_with_baseline.md")
                with open(comp_md, "w", encoding="utf-8") as f:
                    f.write(format_comparative_markdown(comparative_report))

                print(f"      Comparative Report:   {comp_md}")
            except Exception as e:
                print(f"      Warning: Comparative baseline execution encountered: {str(e)}")

    # 7. Packaging Artifacts & Experiment Lineage
    print("\n[7/7] Packaging model artifact and experiment lineage...")
    model_version = f"sift-task-001-transformer-v{dataset_version}"
    artifact_dir = os.path.join(model_output_dir, model_version)

    classifier = SIFTransformerClassifier(
        model=sif_model,
        tokenizer=tokenizer,
        model_version=model_version,
        taxonomy_version="1.0",
        metadata={
            "experiment_id": exp_id,
            "dataset_version": dataset_version,
            "base_model": base_model,
            "max_length": max_length,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "epochs": effective_epochs,
            "device": str(compute_dev),
            "use_class_weights": use_class_weights,
            "is_demo": is_demo,
            "trained_at": datetime.now(timezone.utc).isoformat(),
        },
        device=str(compute_dev),
    )
    classifier.save(artifact_dir)
    print(f"      Model Checkpoint Saved: {artifact_dir}")

    # Build ExperimentRun metadata
    env_info = {
        "python_version": sys.version.split()[0],
        "torch_version": torch.__version__,
        "transformers_version": transformers.__version__,
        "device": str(compute_dev),
        "platform": sys.platform,
    }
    hyperparams = {
        "base_model": base_model,
        "epochs": effective_epochs,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "max_length": max_length,
        "weight_decay": weight_decay,
        "warmup_ratio": warmup_ratio,
        "random_seed": random_seed,
        "use_class_weights": use_class_weights,
        "selection_metric": "0.6*HighSIFRecall + 0.4*MacroF1",
    }

    run_record = ExperimentRun(
        experiment_id=exp_id,
        task="TASK-001",
        dataset_version=dataset_version,
        is_demo_dataset=is_demo,
        model_type=f"Transformer({base_model})",
        feature_type=f"Pretrained Contextual Embeddings (max_seq_len={max_length})",
        hyperparameters=hyperparams,
        training_timestamp=datetime.now(timezone.utc).isoformat(),
        random_seed=random_seed,
        environment=env_info,
        model_artifact_path=artifact_dir,
        notes="DEMO / PIPELINE VALIDATION ONLY" if is_demo else None,
    )

    ExperimentTracker.save_experiment_bundle(
        run=run_record,
        output_dir=exp_dir,
        val_metrics=best_val_metrics,
        test_metrics=test_metrics,
        error_report=error_report,
        predictions=predictions_payload,
    )
    print(f"      Experiment Bundle:      {exp_dir}")

    print("\n" + "=" * 70)
    print(f" [✓] TRANSFORMER BENCHMARK COMPLETE: {base_model}")
    print("=" * 70)

    return classifier, {
        "experiment_id": exp_id,
        "model_artifact": artifact_dir,
        "experiment_dir": exp_dir,
        "val_metrics": best_val_metrics.model_dump() if best_val_metrics else None,
        "test_metrics": test_metrics.model_dump() if test_metrics else None,
        "comparative_report": comparative_report.model_dump() if comparative_report else None,
        "length_audit": length_audit,
    }


def main():
    parser = argparse.ArgumentParser(description="Train SIFT TASK-001 Transformer classification benchmark.")
    parser.add_argument("--train", "-t", required=True, help="Path to train split JSONL")
    parser.add_argument("--val", "--validation", "-v", help="Path to validation split JSONL")
    parser.add_argument("--test", help="Path to test split JSONL")
    parser.add_argument("--base-model", default="distilbert-base-uncased", help="Base pretrained transformer")
    parser.add_argument("--dataset-version", default="0.1.0", help="Dataset version string (default: 0.1.0)")
    parser.add_argument("--output-dir", "-o", default="experiments/task_001", help="Experiment outputs directory")
    parser.add_argument("--model-output", "-m", default="models/task_001/transformer", help="Model artifact destination")
    parser.add_argument("--epochs", type=int, default=3, help="Training epochs")
    parser.add_argument("--batch-size", type=int, default=8, help="Training batch size")
    parser.add_argument("--learning-rate", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--max-length", type=int, default=128, help="Maximum sequence length")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--device", default="auto", help="Compute device: auto, cpu, cuda, mps")
    parser.add_argument("--use-class-weights", action="store_true", default=True, help="Enable class-weighted cross-entropy")
    parser.add_argument("--no-class-weights", dest="use_class_weights", action="store_false", help="Disable class weights")
    parser.add_argument("--smoke-test", action="store_true", help="Run tiny pipeline smoke test")
    parser.add_argument("--demo", action="store_true", help="Flag indicating execution on synthetic demo data")
    parser.add_argument("--classical-model", help="Path to classical baseline model joblib for comparison")

    args = parser.parse_args()

    train_task_001_transformer(
        train_path=args.train,
        val_path=args.val,
        test_path=args.test,
        base_model=args.base_model,
        dataset_version=args.dataset_version,
        output_dir=args.output_dir,
        model_output_dir=args.model_output,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        max_length=args.max_length,
        random_seed=args.seed,
        device=args.device,
        use_class_weights=args.use_class_weights,
        smoke_test=args.smoke_test,
        is_demo=args.demo,
        classical_model_path=args.classical_model,
    )


if __name__ == "__main__":
    main()
