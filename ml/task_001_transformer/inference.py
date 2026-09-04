"""SIFT TASK-001 Transformer Inference Engine & Wrapper.

Provides framework-neutral model loading, single and batch inference returning
standardized SIFClassificationPrediction records, with strict isolation of raw logits
and uncalibrated softmax probabilities.
"""

from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional
import torch

from ml.task_001.schemas import SIFClassificationPrediction, SIFScoreBreakdown
from ml.task_001_transformer.config import (
    TransformerModelConfig,
    detect_compute_device,
    CANONICAL_SIF_CLASSES,
)
from ml.task_001_transformer.model import SIFTransformerModel
from ml.task_001_transformer.tokenizer import SafetyReportTokenizer


class SIFTransformerClassifier:
    """Production-grade inference interface for fine-tuned transformer models."""

    def __init__(
        self,
        model: SIFTransformerModel,
        tokenizer: SafetyReportTokenizer,
        model_version: str = "sift-task-001-transformer-v0.1.0",
        taxonomy_version: str = "1.0",
        metadata: Optional[Dict[str, Any]] = None,
        device: str = "auto",
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.model_version = model_version
        self.taxonomy_version = taxonomy_version
        self.metadata = metadata or {}
        self.device = detect_compute_device(device)

        self.model.to(self.device)
        self.model.eval()

    def predict(self, text: str) -> SIFClassificationPrediction:
        """Predict SIF Potential for a single safety report narrative.
        
        Args:
            text: Unedited raw field safety narrative.
            
        Returns:
            SIFClassificationPrediction object.
        """
        results = self.predict_batch([text])
        return results[0]

    def predict_batch(
        self,
        texts: List[str],
        batch_size: int = 16,
    ) -> List[SIFClassificationPrediction]:
        """Predict SIF Potential for a list of safety report narratives.
        
        Args:
            texts: List of raw safety report text strings.
            batch_size: Batch size for forward inference passes.
            
        Returns:
            List of SIFClassificationPrediction objects.
        """
        if not texts:
            return []

        predictions: List[SIFClassificationPrediction] = []
        id2label = self.model.cfg.id2label

        self.model.eval()
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i : i + batch_size]
                enc = self.tokenizer.encode_batch(batch_texts, return_tensors="pt")
                input_ids = enc["input_ids"].to(self.device)
                attention_mask = enc["attention_mask"].to(self.device)

                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                probs = outputs["probabilities"].cpu().numpy()
                logits = outputs["logits"].cpu().numpy()

                for prob_vec, logit_vec in zip(probs, logits):
                    pred_idx = int(prob_vec.argmax())
                    # Support both integer and string keys in id2label
                    pred_label = id2label.get(pred_idx) or id2label.get(str(pred_idx), "NON-SIF")

                    # Class probabilities dictionary
                    scores_dict: Dict[str, float] = {}
                    for cls_idx in range(len(prob_vec)):
                        cls_name = id2label.get(cls_idx) or id2label.get(str(cls_idx), f"CLASS_{cls_idx}")
                        scores_dict[cls_name] = round(float(prob_vec[cls_idx]), 4)

                    top_confidence = round(float(prob_vec[pred_idx]) * 100.0, 2)

                    predictions.append(SIFClassificationPrediction(
                        task="TASK-001",
                        model_version=self.model_version,
                        predicted_sif_potential=pred_label,
                        confidence=top_confidence,
                        decision_scores=SIFScoreBreakdown(
                            scores=scores_dict,
                            score_type="uncalibrated_probability",
                        ),
                        inference_timestamp=datetime.now(timezone.utc).isoformat(),
                    ))

        return predictions

    def save(self, directory: str):
        """Serialize complete transformer bundle (weights, tokenizer, and metadata).
        
        Args:
            directory: Target output directory (e.g. models/task_001/transformer/v0.1.0).
        """
        os.makedirs(directory, exist_ok=True)
        self.model.save_pretrained(directory)
        self.tokenizer.save_pretrained(directory)

        meta = {
            "model_version": self.model_version,
            "taxonomy_version": self.taxonomy_version,
            "model_family": "transformer",
            "base_model": self.model.cfg.base_model,
            "max_length": self.tokenizer.max_length,
            "num_parameters": self.model.num_parameters,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "metadata": self.metadata,
        }
        with open(os.path.join(directory, "sift_model_meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

    @classmethod
    def load(
        cls,
        directory: str,
        device: str = "auto",
    ) -> "SIFTransformerClassifier":
        """Load fine-tuned transformer and tokenizer from serialized directory.
        
        Args:
            directory: Directory containing saved model checkpoint.
            device: Compute device string.
            
        Returns:
            Instantiated SIFTransformerClassifier.
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Transformer model directory not found: {directory}")

        meta_path = os.path.join(directory, "sift_model_meta.json")
        meta = {}
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

        model = SIFTransformerModel.from_pretrained(directory)
        max_length = meta.get("max_length", 128)
        tokenizer = SafetyReportTokenizer.from_pretrained(directory, max_length=max_length)

        return cls(
            model=model,
            tokenizer=tokenizer,
            model_version=meta.get("model_version", "sift-task-001-transformer"),
            taxonomy_version=meta.get("taxonomy_version", "1.0"),
            metadata=meta.get("metadata", {}),
            device=device,
        )
