"""SIFT Classification Metrics, Multiclass Evaluation & Confusion Matrix Generator.

Computes precision, recall, macro/weighted F1, safety-critical High-SIF recall,
and renders clean Matplotlib confusion matrix visualizations.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt


CANONICAL_SIF_CLASSES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "NON-SIF"]


class ClassMetric(BaseModel):
    """Per-class performance breakdown."""
    class_name: str
    support: int
    precision: float
    recall: float
    f1_score: float


class ClassificationMetrics(BaseModel):
    """Multidimensional model performance metrics."""
    total_samples: int
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_f1: float
    high_sif_recall: float
    high_sif_support: int
    high_sif_correct: int
    per_class_metrics: List[ClassMetric]
    confusion_matrix_classes: List[str]
    confusion_matrix_grid: List[List[int]]


def compute_classification_metrics(
    y_true: List[str],
    y_pred: List[str],
    classes: Optional[List[str]] = None,
) -> ClassificationMetrics:
    """Compute complete classification metrics including safety-critical High-SIF recall.
    
    Args:
        y_true: True ground truth labels.
        y_pred: Predicted labels from model.
        classes: Ordered list of classes. Defaults to CANONICAL_SIF_CLASSES filtered to present.
        
    Returns:
        ClassificationMetrics instance.
    """
    n = len(y_true)
    if n == 0:
        return ClassificationMetrics(
            total_samples=0,
            accuracy=0.0,
            macro_precision=0.0,
            macro_recall=0.0,
            macro_f1=0.0,
            weighted_f1=0.0,
            high_sif_recall=0.0,
            high_sif_support=0,
            high_sif_correct=0,
            per_class_metrics=[],
            confusion_matrix_classes=[],
            confusion_matrix_grid=[],
        )

    # Determine active classes
    unique_present = sorted(list(set(y_true).union(set(y_pred))))
    if classes is None:
        # Keep canonical order for known classes, append any others
        ordered = [c for c in CANONICAL_SIF_CLASSES if c in unique_present]
        for c in unique_present:
            if c not in ordered:
                ordered.append(c)
        classes = ordered

    acc = float(accuracy_score(y_true, y_pred))

    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=classes, average="macro", zero_division=0
    )
    _, _, f1_weighted, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=classes, average="weighted", zero_division=0
    )

    p_per, r_per, f_per, s_per = precision_recall_fscore_support(
        y_true, y_pred, labels=classes, average=None, zero_division=0
    )

    per_class_list: List[ClassMetric] = []
    for c_name, p, r, f, s in zip(classes, p_per, r_per, f_per, s_per):
        per_class_list.append(ClassMetric(
            class_name=c_name,
            support=int(s),
            precision=round(float(p), 4),
            recall=round(float(r), 4),
            f1_score=round(float(f), 4),
        ))

    # Compute Safety-Critical High-SIF Recall (CRITICAL + HIGH combined)
    high_sif_targets = {"CRITICAL", "HIGH"}
    high_sif_actual_indices = [i for i, y in enumerate(y_true) if y in high_sif_targets]
    high_sif_support = len(high_sif_actual_indices)
    high_sif_correct = sum(
        1 for i in high_sif_actual_indices if y_pred[i] in high_sif_targets
    )
    high_sif_recall = (high_sif_correct / high_sif_support) if high_sif_support > 0 else 0.0

    # Compute confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=classes)
    cm_grid = cm.tolist()

    return ClassificationMetrics(
        total_samples=n,
        accuracy=round(acc, 4),
        macro_precision=round(float(prec_macro), 4),
        macro_recall=round(float(rec_macro), 4),
        macro_f1=round(float(f1_macro), 4),
        weighted_f1=round(float(f1_weighted), 4),
        high_sif_recall=round(float(high_sif_recall), 4),
        high_sif_support=high_sif_support,
        high_sif_correct=high_sif_correct,
        per_class_metrics=per_class_list,
        confusion_matrix_classes=classes,
        confusion_matrix_grid=cm_grid,
    )


def generate_confusion_matrix_plot(
    metrics: ClassificationMetrics,
    output_path: str,
    title: str = "SIFT SIF Potential Confusion Matrix",
):
    """Render and save a clean, professional Matplotlib confusion matrix image."""
    classes = metrics.confusion_matrix_classes
    cm = np.array(metrics.confusion_matrix_grid)

    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)

    ax.set(
        xticks=np.arange(cm.shape[1]),
        yticks=np.arange(cm.shape[0]),
        xticklabels=classes,
        yticklabels=classes,
        title=title,
        ylabel="Actual True Label",
        xlabel="Model Predicted Label",
    )

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Loop over data dimensions and create text annotations
    thresh = cm.max() / 2.0 if cm.max() > 0 else 1.0
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, format(cm[i, j], "d"),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black",
                fontweight="bold"
            )

    fig.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
