"""SIFT TASK-001 Inference Engine & Model Wrapper.

Provides framework-neutral serialization, loading, and batch inference interfaces
returning structured SIFClassificationPrediction records.
"""

from datetime import datetime, timezone
import os
from typing import Any, Dict, List, Optional
import joblib

from ml.task_001.schemas import SIFClassificationPrediction, SIFScoreBreakdown
from ml.task_001.features import TfidfFeatureExtractor
from ml.task_001.models import BaseSIFModel


class SIFClassifier:
    """Production-ready inference wrapper for TASK-001 SIF Potential classification."""

    def __init__(
        self,
        extractor: TfidfFeatureExtractor,
        model: BaseSIFModel,
        model_version: str = "sift-task-001-baseline-v0.1.0",
        taxonomy_version: str = "1.0",
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.extractor = extractor
        self.model = model
        self.model_version = model_version
        self.taxonomy_version = taxonomy_version
        self.metadata = metadata or {}

    def predict(self, text: str) -> SIFClassificationPrediction:
        """Predict SIF Potential for a single safety report narrative.
        
        Args:
            text: Unedited raw field narrative.
            
        Returns:
            SIFClassificationPrediction object.
        """
        results = self.predict_batch([text])
        return results[0]

    def predict_batch(self, texts: List[str]) -> List[SIFClassificationPrediction]:
        """Predict SIF Potential for a batch of safety narratives.
        
        Args:
            texts: List of raw text narratives.
            
        Returns:
            List of SIFClassificationPrediction objects.
        """
        if not texts:
            return []

        # 1. Transform texts via training-fitted TF-IDF
        X = self.extractor.transform(texts)

        # 2. Predict labels
        preds = self.model.predict(X)

        # 3. Compute score breakdown
        scores_list, score_type = self.model.predict_scores(X)

        predictions: List[SIFClassificationPrediction] = []
        for pred_label, scores in zip(preds, scores_list):
            # Calculate a confidence score
            conf = None
            if score_type == "uncalibrated_probability":
                conf = round(scores.get(pred_label, 0.0) * 100.0, 2)
            elif score_type == "decision_score":
                # Scale raw margin to a 0-100 heuristic
                raw_score = scores.get(pred_label, 0.0)
                # Softmax-like or sigmoid mapping for display
                conf = round(float(1.0 / (1.0 + 2.71828 ** (-raw_score))) * 100.0, 2)

            predictions.append(SIFClassificationPrediction(
                task="TASK-001",
                model_version=self.model_version,
                predicted_sif_potential=pred_label,
                confidence=conf,
                decision_scores=SIFScoreBreakdown(
                    scores=scores,
                    score_type=score_type,
                ),
                inference_timestamp=datetime.now(timezone.utc).isoformat(),
            ))

        return predictions

    def save(self, filepath: str):
        """Serialize complete model bundle to disk using joblib.
        
        Args:
            filepath: Destination path (e.g. 'models/task_001/model.joblib').
        """
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        bundle = {
            "extractor": self.extractor,
            "model": self.model,
            "model_version": self.model_version,
            "taxonomy_version": self.taxonomy_version,
            "metadata": self.metadata,
        }
        joblib.dump(bundle, filepath)

    @classmethod
    def load(cls, filepath: str) -> "SIFClassifier":
        """Load serialized model bundle from disk.
        
        Args:
            filepath: Path to .joblib artifact.
            
        Returns:
            Instantiated SIFClassifier.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model artifact not found at: {filepath}")
        bundle = joblib.load(filepath)
        return cls(
            extractor=bundle["extractor"],
            model=bundle["model"],
            model_version=bundle.get("model_version", "unknown"),
            taxonomy_version=bundle.get("taxonomy_version", "1.0"),
            metadata=bundle.get("metadata", {}),
        )
