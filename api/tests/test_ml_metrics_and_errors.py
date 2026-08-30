"""Tests for SIFT Multiclass Metrics, High-SIF Recall & False-Negative Analyzer."""

import os
import tempfile
import pytest

from ml.common.metrics import compute_classification_metrics, generate_confusion_matrix_plot
from ml.common.errors import FalseNegativeAnalyzer


def test_high_sif_recall_calculation():
    """Verify exact calculation of safety-critical High-SIF recall."""
    y_true = ["CRITICAL", "HIGH", "HIGH", "MEDIUM", "LOW", "NON-SIF"]
    # Model correctly predicts 2 out of 3 High-SIF cases
    y_pred = ["CRITICAL", "HIGH", "LOW", "MEDIUM", "LOW", "NON-SIF"]

    metrics = compute_classification_metrics(y_true, y_pred)
    assert metrics.total_samples == 6
    assert metrics.high_sif_support == 3
    assert metrics.high_sif_correct == 2
    assert pytest.approx(metrics.high_sif_recall, 0.001) == 2.0 / 3.0  # 66.67%


def test_confusion_matrix_plot_generation(tmp_path):
    """Verify Matplotlib renders and saves valid confusion matrix PNG."""
    y_true = ["CRITICAL", "HIGH", "LOW", "NON-SIF"]
    y_pred = ["CRITICAL", "MEDIUM", "LOW", "NON-SIF"]

    metrics = compute_classification_metrics(y_true, y_pred)
    plot_file = tmp_path / "test_cm.png"
    generate_confusion_matrix_plot(metrics, str(plot_file))

    assert plot_file.exists()
    assert plot_file.stat().st_size > 1000


def test_false_negative_analyzer():
    """Verify isolation of High-SIF false negatives and diagnostic assignment."""
    report_ids = ["REC-01", "REC-02", "REC-03"]
    texts = [
        "45 bar pressurized gas blowout on compressor line.",
        "Worker slipped on gravel path and scraped elbow.",
        "Scaffold worker without harness tie-off at 9 meters.",
    ]
    y_true = ["CRITICAL", "LOW", "HIGH"]
    # REC-03 (HIGH) misclassified as NON-SIF is a High-SIF False Negative
    y_pred = ["CRITICAL", "LOW", "NON-SIF"]

    report = FalseNegativeAnalyzer.analyze(report_ids, texts, y_true, y_pred)

    assert report.total_samples == 3
    assert report.total_misclassifications == 1
    assert report.total_high_sif_false_negatives == 1
    assert len(report.false_negative_records) == 1
    fn = report.false_negative_records[0]
    assert fn.report_id == "REC-03"
    assert fn.actual_label == "HIGH"
    assert fn.predicted_label == "NON-SIF"
