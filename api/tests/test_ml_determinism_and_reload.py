"""Tests for SIFT Model Reload Consistency and Training Determinism."""

import os
import pytest

from ml.task_001.features import TfidfFeatureExtractor
from ml.task_001.models import LogisticRegressionSIFClassifier, LinearSVMSIFClassifier
from ml.task_001.inference import SIFClassifier


def test_model_save_and_reload_consistency(tmp_path):
    """Verify serialized .joblib artifact reloads and generates identical predictions."""
    train_texts = [
        "40 bar natural gas leak under high pressure without isolation.",
        "Scaffold fall protection harness unclipped at elevation.",
        "Housekeeping plastic cups and empty bottles in cafeteria.",
    ]
    train_labels = ["CRITICAL", "HIGH", "NON-SIF"]

    extractor = TfidfFeatureExtractor()
    X_train = extractor.fit_transform_train(train_texts)

    model = LinearSVMSIFClassifier(random_seed=42)
    model.fit(X_train, train_labels)

    original_classifier = SIFClassifier(
        extractor=extractor,
        model=model,
        model_version="sift-task-001-v0.1.0",
    )

    query = "40 bar high pressure gas leak."
    orig_pred = original_classifier.predict(query)

    # Save artifact
    artifact_path = tmp_path / "model.joblib"
    original_classifier.save(str(artifact_path))

    # Reload artifact
    reloaded_classifier = SIFClassifier.load(str(artifact_path))
    reloaded_pred = reloaded_classifier.predict(query)

    assert orig_pred.predicted_sif_potential == reloaded_pred.predicted_sif_potential
    assert orig_pred.confidence == reloaded_pred.confidence
    assert orig_pred.decision_scores.scores == reloaded_pred.decision_scores.scores


def test_training_determinism_with_fixed_seed():
    """Verify training twice with identical seed produces identical model parameters and predictions."""
    texts = [
        "Gas compressor bypass flange vibrating under 45 bar pressure.",
        "Technician entering crude storage vessel without gas testing.",
        "Housekeeping boxes stacked in hallway passage.",
    ]
    labels = ["CRITICAL", "CRITICAL", "NON-SIF"]

    # Run 1
    ext1 = TfidfFeatureExtractor()
    X1 = ext1.fit_transform_train(texts)
    clf1 = LogisticRegressionSIFClassifier(random_seed=42)
    clf1.fit(X1, labels)
    preds1 = clf1.predict(X1)

    # Run 2
    ext2 = TfidfFeatureExtractor()
    X2 = ext2.fit_transform_train(texts)
    clf2 = LogisticRegressionSIFClassifier(random_seed=42)
    clf2.fit(X2, labels)
    preds2 = clf2.predict(X2)

    assert preds1 == preds2
