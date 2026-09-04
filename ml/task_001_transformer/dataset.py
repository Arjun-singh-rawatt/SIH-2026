"""SIFT PyTorch Dataset & Class Weighting Utilities.

Converts SIFT LoadedDatasetSplit records into tokenized PyTorch Tensors and computes
inverse-frequency class weightings to counteract severe industrial safety imbalances.
"""

from collections import Counter
from typing import Any, Dict, List, Optional
import torch
from torch.utils.data import Dataset

from ml.task_001_transformer.tokenizer import SafetyReportTokenizer
from ml.task_001_transformer.config import DEFAULT_LABEL2ID


def compute_class_weights(
    labels: List[str],
    label2id: Optional[Dict[str, int]] = None,
    num_classes: Optional[int] = None,
) -> torch.Tensor:
    """Compute inverse-frequency class weights from training labels.
    
    Formula: weight_c = total_samples / (num_active_classes * count_c)
    
    Args:
        labels: List of ground-truth label strings from training partition.
        label2id: Mapping from label string to integer index.
        num_classes: Total number of classes in taxonomy.
        
    Returns:
        torch.FloatTensor of shape (num_classes,).
    """
    mapping = label2id or DEFAULT_LABEL2ID
    k = num_classes or len(mapping)
    total = len(labels)
    if total == 0:
        return torch.ones(k, dtype=torch.float32)

    counts = Counter(labels)
    weights = torch.ones(k, dtype=torch.float32)

    active_classes = len(counts)
    if active_classes == 0:
        return weights

    for label_str, class_idx in mapping.items():
        cnt = counts.get(label_str, 0)
        if cnt > 0:
            w = total / (active_classes * cnt)
            weights[class_idx] = float(w)
        else:
            # For unobserved classes in small demo data, assign default neutral weight
            weights[class_idx] = 1.0

    # Normalize weights so their average is 1.0 across active classes
    active_weights = [weights[mapping[lbl]] for lbl in counts.keys() if lbl in mapping]
    if active_weights:
        mean_w = sum(active_weights) / len(active_weights)
        if mean_w > 0:
            weights = weights / mean_w

    return weights


class SIFTextDataset(Dataset):
    """PyTorch Dataset wrapper for SIFT safety narratives."""

    def __init__(
        self,
        texts: List[str],
        labels: Optional[List[str]] = None,
        report_ids: Optional[List[str]] = None,
        tokenizer: Optional[SafetyReportTokenizer] = None,
        label2id: Optional[Dict[str, int]] = None,
        max_length: Optional[int] = None,
    ):
        self.texts = texts
        self.labels = labels
        self.report_ids = report_ids
        self.tokenizer = tokenizer or SafetyReportTokenizer(max_length=max_length or 128)
        self.label2id = label2id or DEFAULT_LABEL2ID
        self.max_length = max_length

    def __len__(self) -> int:
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        text = self.texts[idx]
        enc = self.tokenizer.encode(
            text,
            max_length=self.max_length,
            return_tensors="pt",
        )

        item = {
            "input_ids": enc["input_ids"].squeeze(0),
            "attention_mask": enc["attention_mask"].squeeze(0),
            "raw_text": text,
        }

        if self.report_ids and idx < len(self.report_ids):
            item["report_id"] = self.report_ids[idx]
        else:
            item["report_id"] = f"RECORD-{idx}"

        if self.labels is not None and idx < len(self.labels):
            lbl = self.labels[idx]
            lbl_id = self.label2id.get(lbl, 0)
            item["label"] = torch.tensor(lbl_id, dtype=torch.long)

        return item
