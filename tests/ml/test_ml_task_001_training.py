"""Tests for SIFT TASK-001 Training Pipeline & Standalone Evaluation."""

import os
import shutil
import tempfile
import pytest

from ml.task_001.train import train_task_001_baseline
from ml.task_001.evaluate import evaluate_model


def test_task_001_training_pipeline_execution():
    """Verify end-to-end training, candidate evaluation, model selection, and artifact saving."""
    train_fixture = os.path.abspath("data/fixtures/sample_ml_train.jsonl")
    test_fixture = os.path.abspath("data/fixtures/sample_ml_test.jsonl")
    temp_dir = tempfile.mkdtemp()
    model_dir = os.path.join(temp_dir, "models")
    exp_dir = os.path.join(temp_dir, "experiments")

    try:
        classifier, results = train_task_001_baseline(
            train_path=train_fixture,
            val_path=train_fixture,
            test_path=test_fixture,
            dataset_version="0.1.0",
            output_dir=exp_dir,
            model_output_dir=model_dir,
            random_seed=42,
            is_demo=True,
        )

        assert classifier is not None
        assert os.path.exists(results["model_artifact"])
        assert results["test_metrics"] is not None
        assert "accuracy" in results["test_metrics"]
        assert "high_sif_recall" in results["test_metrics"]

        # Check generated files in experiment directory
        exp_root = results["experiment_dir"]
        assert os.path.exists(os.path.join(exp_root, "experiment.json"))
        assert os.path.exists(os.path.join(exp_root, "metrics.json"))
        assert os.path.exists(os.path.join(exp_root, "metrics.md"))
        assert os.path.exists(os.path.join(exp_root, "confusion_matrix.png"))

        # Test standalone evaluate_model CLI function on saved artifact
        eval_out = os.path.join(temp_dir, "eval_out")
        evaluate_model(results["model_artifact"], test_fixture, output_dir=eval_out)
        assert os.path.exists(os.path.join(eval_out, "eval_metrics.json"))
        assert os.path.exists(os.path.join(eval_out, "eval_confusion_matrix.png"))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
