"""Configuration schemas and device detection for SIFT TASK-001 Transformer Benchmark."""

import os
import sys
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import torch

# Ensure api directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api")))

from app.schemas.ai.taxonomy import SIFPotentialLevel

CANONICAL_SIF_CLASSES = [e.value for e in SIFPotentialLevel]
DEFAULT_LABEL2ID = {name: idx for idx, name in enumerate(CANONICAL_SIF_CLASSES)}
DEFAULT_ID2LABEL = {idx: name for idx, name in enumerate(CANONICAL_SIF_CLASSES)}


def detect_compute_device(requested_device: str = "auto") -> torch.device:
    """Detect available compute device with fallback mechanism.
    
    Args:
        requested_device: 'auto', 'cuda', 'mps', or 'cpu'.
        
    Returns:
        torch.device instance.
    """
    req = requested_device.lower().strip()
    if req == "cuda":
        if torch.cuda.is_available():
            return torch.device("cuda")
        return torch.device("cpu")
    elif req == "mps":
        if torch.backends.mps.is_available():
            return torch.device("mps")
        return torch.device("cpu")
    elif req == "cpu":
        return torch.device("cpu")
    
    # Auto-detection: CUDA -> MPS -> CPU
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


class TransformerModelConfig(BaseModel):
    """Model architecture configuration."""
    base_model: str = Field(
        default="distilbert-base-uncased",
        description="Hugging Face pretrained encoder name or local path",
    )
    num_labels: int = Field(default=len(CANONICAL_SIF_CLASSES))
    max_length: int = Field(default=128, description="Maximum sequence length after tokenization")
    label2id: Dict[str, int] = Field(default_factory=lambda: DEFAULT_LABEL2ID.copy())
    id2label: Dict[int, str] = Field(default_factory=lambda: DEFAULT_ID2LABEL.copy())
    problem_type: str = Field(default="single_label_classification")


class TrainingConfig(BaseModel):
    """Hyperparameter and training execution configuration."""
    learning_rate: float = Field(default=2e-5, description="Initial learning rate for AdamW")
    batch_size: int = Field(default=8, description="Batch size for training and evaluation")
    epochs: int = Field(default=3, description="Number of full training epochs")
    weight_decay: float = Field(default=0.01, description="L2 weight decay for AdamW")
    warmup_ratio: float = Field(default=0.1, description="Proportion of training steps for linear warmup")
    random_seed: int = Field(default=42, description="Random seed for reproducibility")
    device: str = Field(default="auto", description="Compute device: auto, cpu, cuda, mps")
    use_class_weights: bool = Field(
        default=True,
        description="Whether to use inverse-frequency class weighting in loss function",
    )
    selection_metric: str = Field(
        default="high_sif_recall_macro_f1",
        description="Validation metric for checkpoint selection (0.6 * high_sif_recall + 0.4 * macro_f1)",
    )
    smoke_test: bool = Field(
        default=False,
        description="Pipeline smoke-test mode with synthetic batches",
    )
    is_demo: bool = Field(
        default=False,
        description="Flag indicating execution on demo / synthetic datasets",
    )
