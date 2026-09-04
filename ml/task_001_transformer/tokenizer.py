"""SIFT Safety Report Tokenizer & Sequence Length Auditor.

Wraps Hugging Face AutoTokenizer for safety narratives, enforces strict padding,
truncation, and attention mask generation, and computes report length distributions.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from transformers import AutoTokenizer


class SafetyReportTokenizer:
    """Specialized tokenizer wrapper for SIFT safety observations."""

    def __init__(
        self,
        model_name_or_path: str = "distilbert-base-uncased",
        max_length: int = 128,
        tokenizer: Optional[Any] = None,
    ):
        self.model_name_or_path = model_name_or_path
        self.max_length = max_length
        if tokenizer is not None:
            self._tokenizer = tokenizer
        else:
            self._tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

    @property
    def tokenizer(self) -> Any:
        """Underlying Hugging Face tokenizer."""
        return self._tokenizer

    @property
    def vocab_size(self) -> int:
        """Vocabulary size of tokenizer."""
        return getattr(self._tokenizer, "vocab_size", len(self._tokenizer))

    def encode(
        self,
        text: str,
        max_length: Optional[int] = None,
        return_tensors: Optional[str] = "pt",
    ) -> Dict[str, Any]:
        """Tokenize a single safety report narrative."""
        length = max_length or self.max_length
        return self._tokenizer(
            text,
            max_length=length,
            padding="max_length",
            truncation=True,
            return_attention_mask=True,
            return_tensors=return_tensors,
        )

    def encode_batch(
        self,
        texts: List[str],
        max_length: Optional[int] = None,
        padding: bool = True,
        truncation: bool = True,
        return_tensors: Optional[str] = "pt",
    ) -> Dict[str, Any]:
        """Tokenize a batch of safety report narratives."""
        length = max_length or self.max_length
        pad_strategy = "max_length" if padding else False
        return self._tokenizer(
            texts,
            max_length=length,
            padding=pad_strategy,
            truncation=truncation,
            return_attention_mask=True,
            return_tensors=return_tensors,
        )

    def analyze_length_distribution(
        self,
        texts: List[str],
        max_length: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Audit word, character, and subword token lengths across a text collection.
        
        Args:
            texts: List of safety report narrative strings.
            max_length: Maximum sequence length boundary to evaluate truncation impact.
            
        Returns:
            Dictionary containing length distribution quantiles and truncation counts.
        """
        eval_max_length = max_length or self.max_length
        if not texts:
            return {
                "total_reports": 0,
                "character_distribution": {},
                "word_distribution": {},
                "token_distribution": {},
                "truncated_reports_count": 0,
                "truncated_percentage": 0.0,
            }

        char_lens = [len(t) for t in texts]
        word_lens = [len(t.split()) for t in texts]

        # Subword token lengths without truncation
        token_lens: List[int] = []
        for t in texts:
            try:
                tokens = self._tokenizer.encode(t, truncation=False, add_special_tokens=True)
                token_lens.append(len(tokens))
            except Exception:
                token_lens.append(len(t.split()))

        truncated_count = sum(1 for tl in token_lens if tl > eval_max_length)
        pct_truncated = round((truncated_count / len(texts)) * 100.0, 2)

        def _stats(arr: List[int]) -> Dict[str, float]:
            return {
                "min": int(np.min(arr)),
                "median": float(np.median(arr)),
                "p75": float(np.percentile(arr, 75)),
                "p90": float(np.percentile(arr, 90)),
                "p95": float(np.percentile(arr, 95)),
                "max": int(np.max(arr)),
            }

        return {
            "total_reports": len(texts),
            "max_sequence_length_configured": eval_max_length,
            "character_distribution": _stats(char_lens),
            "word_distribution": _stats(word_lens),
            "token_distribution": _stats(token_lens),
            "truncated_reports_count": truncated_count,
            "truncated_percentage": pct_truncated,
        }

    def save_pretrained(self, save_directory: str):
        """Save tokenizer files to destination directory."""
        self._tokenizer.save_pretrained(save_directory)

    @classmethod
    def from_pretrained(
        cls,
        model_name_or_path: str,
        max_length: int = 128,
    ) -> "SafetyReportTokenizer":
        """Load tokenizer from pretrained path or model identifier."""
        tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        return cls(
            model_name_or_path=model_name_or_path,
            max_length=max_length,
            tokenizer=tokenizer,
        )
