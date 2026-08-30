"""SIFT TASK-001: SIF Potential Classification Baseline.

Classical machine learning models (TF-IDF + Logistic Regression & Linear SVM)
for predicting Serious Injury or Fatality (SIF) potential from unstructured text.
"""

from ml.task_001.schemas import SIFClassificationPrediction, SIFScoreBreakdown
from ml.task_001.features import TfidfFeatureExtractor, TfidfConfig
from ml.task_001.models import (
    BaseSIFModel,
    LogisticRegressionSIFClassifier,
    LinearSVMSIFClassifier,
    build_candidate_models,
)
from ml.task_001.inference import SIFClassifier

__all__ = [
    "SIFClassificationPrediction",
    "SIFScoreBreakdown",
    "TfidfFeatureExtractor",
    "TfidfConfig",
    "BaseSIFModel",
    "LogisticRegressionSIFClassifier",
    "LinearSVMSIFClassifier",
    "build_candidate_models",
    "SIFClassifier",
]
