"""SIFT Transformer Classification Model Architecture.

Encapsulates sequence classification encoder with customizable loss objectives
(standard multinomial cross-entropy vs class-weighted cross-entropy).
"""

from typing import Any, Dict, Optional
import torch
import torch.nn as nn
from transformers import AutoModelForSequenceClassification, AutoConfig

from ml.task_001_transformer.config import (
    TransformerModelConfig,
    DEFAULT_ID2LABEL,
    DEFAULT_LABEL2ID,
)


class SIFTransformerModel(nn.Module):
    """Transformer sequence classification model for safety potential prediction."""

    def __init__(
        self,
        config: Optional[TransformerModelConfig] = None,
        encoder: Optional[nn.Module] = None,
        class_weights: Optional[torch.Tensor] = None,
    ):
        super().__init__()
        self.cfg = config or TransformerModelConfig()
        self.class_weights = class_weights

        if encoder is not None:
            self.encoder = encoder
        else:
            self.encoder = AutoModelForSequenceClassification.from_pretrained(
                self.cfg.base_model,
                num_labels=self.cfg.num_labels,
                id2label=self.cfg.id2label,
                label2id=self.cfg.label2id,
            )

    @property
    def num_parameters(self) -> int:
        """Total number of parameters in the model."""
        return sum(p.numel() for p in self.encoder.parameters())

    @property
    def trainable_parameters(self) -> int:
        """Total number of trainable parameters in the model."""
        return sum(p.numel() for p in self.encoder.parameters() if p.requires_grad)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """Forward pass through encoder and classification head.
        
        Args:
            input_ids: Tensor of token ids (batch_size, seq_len).
            attention_mask: Attention mask (batch_size, seq_len).
            labels: Ground-truth target indices (batch_size,).
            
        Returns:
            Dictionary containing 'logits', 'probabilities', and optional 'loss'.
        """
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask,
        )
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)

        loss = None
        if labels is not None:
            if self.class_weights is not None:
                weights = self.class_weights.to(logits.device)
                loss_fct = nn.CrossEntropyLoss(weight=weights)
            else:
                loss_fct = nn.CrossEntropyLoss()
            loss = loss_fct(logits.view(-1, self.cfg.num_labels), labels.view(-1))

        return {
            "loss": loss,
            "logits": logits,
            "probabilities": probs,
        }

    def save_pretrained(self, save_directory: str):
        """Serialize encoder weights and configuration to disk."""
        self.encoder.save_pretrained(save_directory)

    @classmethod
    def from_pretrained(
        cls,
        model_directory: str,
        class_weights: Optional[torch.Tensor] = None,
    ) -> "SIFTransformerModel":
        """Load fine-tuned model checkpoint from local directory."""
        encoder = AutoModelForSequenceClassification.from_pretrained(model_directory)
        cfg = TransformerModelConfig(
            base_model=model_directory,
            num_labels=encoder.config.num_labels,
            id2label=encoder.config.id2label,
            label2id=encoder.config.label2id,
        )
        return cls(config=cfg, encoder=encoder, class_weights=class_weights)
