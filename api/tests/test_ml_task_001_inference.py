"""Tests for SIFT TASK-001 Inference Wrapper & Prediction Contracts."""

import pytest
from ml.task_001.features import TfidfFeatureExtractor
from ml.task_001.models import LogisticRegressionSIFClassifier
from ml.task_001.inference import SIFClassifier
from ml.task_001.schemas import SIFClassificationPrediction


def test_sif_classifier_single_and_batch_prediction():
    """Verify single and batch prediction contracts conform to SIFClassificationPrediction schema."""
    train_texts = [
        "40 bar natural gas leak under high pressure without isolation.",
        "Scaffold fall protection harness unclipped at elevation.",
        "Housekeeping plastic cups and empty bottles in cafeteria.",
    ]
    train_labels = ["CRITICAL", "HIGH", "NON-SIF"]

    extractor = TfidfFeatureExtractor()
    X_train = extractor.fit_transform_train(train_texts)

    model = LogisticRegressionSIFClassifier(random_seed=42)
    model.fit(X_train, train_labels)

    classifier = SIFClassifier(
        extractor=extractor,
        model=model,
        model_version="sift-task-001-test-v1.0",
    )

    # 1. Single prediction
    pred = classifier.predict("35 bar gas line pressure blowout.")
    assert isinstance(pred, SIFClassificationPrediction)
    assert pred.task == "TASK-001"
    assert pred.predicted_sif_potential in {"CRITICAL", "HIGH", "NON-SIF"}
    assert pred.confidence is not None
    assert "CRITICAL" in pred.decision_scores.scores

    # 2. Batch prediction
    batch_preds = classifier.predict_batch([
        "Working on scaffold at 10m height.",
        "Empty cardboard box on walkway.",
    ])
    assert len(batch_preds) == 2
    assert all(isinstance(p, SIFClassificationPrediction) for p in batch_preds)
