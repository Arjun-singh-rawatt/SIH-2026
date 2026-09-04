"""Unit tests for SIFT TASK-001 Pretrained Transformer Benchmark.

Runs entirely OFFLINE with ZERO network dependency using lightweight mock
tokenizers and tiny local PyTorch models.
"""

import json
import os
import sys
import tempfile
import pytest
import torch
import torch.nn as nn
from transformers import DistilBertConfig, DistilBertForSequenceClassification

# Ensure root and api are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "api")))

from ml.task_001_transformer.config import (
    TransformerModelConfig,
    TrainingConfig,
    detect_compute_device,
    CANONICAL_SIF_CLASSES,
    DEFAULT_LABEL2ID,
    DEFAULT_ID2LABEL,
)
from ml.task_001_transformer.tokenizer import SafetyReportTokenizer
from ml.task_001_transformer.dataset import SIFTextDataset, compute_class_weights
from ml.task_001_transformer.model import SIFTransformerModel
from ml.task_001_transformer.inference import SIFTransformerClassifier
from ml.task_001_transformer.comparison import (
    generate_comparative_report,
    format_comparative_markdown,
)
from ml.common.metrics import compute_classification_metrics
from ml.common.errors import FalseNegativeAnalyzer


class TinyMockTokenizer:
    """Zero-network deterministic mock tokenizer for testing."""

    def __init__(self, vocab_size: int = 100, max_length: int = 32):
        self.vocab_size = vocab_size
        self.max_length = max_length

    def __len__(self):
        return self.vocab_size

    def encode(self, text: str, truncation: bool = False, add_special_tokens: bool = True):
        # Deterministic token sequence based on word lengths
        tokens = [1] + [(hash(w) % (self.vocab_size - 3)) + 2 for w in text.split()] + [2]
        if truncation and len(tokens) > self.max_length:
            tokens = tokens[:self.max_length]
        return tokens

    def __call__(
        self,
        texts,
        max_length: int = 32,
        padding: str = "max_length",
        truncation: bool = True,
        return_attention_mask: bool = True,
        return_tensors: str = "pt",
    ):
        single = isinstance(texts, str)
        text_list = [texts] if single else texts

        all_input_ids = []
        all_masks = []

        for t in text_list:
            tokens = self.encode(t, truncation=truncation)
            if len(tokens) > max_length and truncation:
                tokens = tokens[:max_length]
            mask = [1] * len(tokens)

            if padding == "max_length" and len(tokens) < max_length:
                pad_len = max_length - len(tokens)
                tokens = tokens + [0] * pad_len
                mask = mask + [0] * pad_len

            all_input_ids.append(tokens)
            all_masks.append(mask)

        if return_tensors == "pt":
            input_ids = torch.tensor(all_input_ids, dtype=torch.long)
            masks = torch.tensor(all_masks, dtype=torch.long)
        else:
            input_ids = all_input_ids
            masks = all_masks

        return {
            "input_ids": input_ids,
            "attention_mask": masks,
        }

    def save_pretrained(self, directory: str):
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, "tokenizer_config.json"), "w") as f:
            json.dump({"mock": True, "vocab_size": self.vocab_size}, f)


@pytest.fixture
def tiny_transformer_model():
    """Build a tiny 1-layer, 32-dim local DistilBERT model for fast offline tests."""
    cfg = DistilBertConfig(
        vocab_size=100,
        max_position_embeddings=128,
        n_layers=1,
        n_heads=2,
        dim=32,
        hidden_dim=64,
        num_labels=5,
        id2label=DEFAULT_ID2LABEL,
        label2id=DEFAULT_LABEL2ID,
    )
    encoder = DistilBertForSequenceClassification(cfg)
    return SIFTransformerModel(
        config=TransformerModelConfig(
            base_model="tiny-mock",
            num_labels=5,
            max_length=32,
            id2label=DEFAULT_ID2LABEL,
            label2id=DEFAULT_LABEL2ID,
        ),
        encoder=encoder,
    )


def test_device_detection():
    """Verify device selection with explicit values and auto-fallback."""
    cpu_dev = detect_compute_device("cpu")
    assert cpu_dev.type == "cpu"

    auto_dev = detect_compute_device("auto")
    assert auto_dev.type in {"cpu", "mps", "cuda"}


def test_tokenizer_wrapper_and_length_audit():
    """Verify tokenizer wrapping, tensor generation, and length distribution calculation."""
    mock_tok = TinyMockTokenizer(vocab_size=100, max_length=16)
    tokenizer = SafetyReportTokenizer(max_length=16, tokenizer=mock_tok)

    texts = [
        "Hydrocarbon leak on manifold line 4",
        "Routine housekeeping inspection completed with no hazards found",
        "Short note",
    ]

    enc = tokenizer.encode(texts[0], return_tensors="pt")
    assert "input_ids" in enc
    assert "attention_mask" in enc
    assert enc["input_ids"].shape == (1, 16)
    assert enc["attention_mask"].shape == (1, 16)

    batch_enc = tokenizer.encode_batch(texts, return_tensors="pt")
    assert batch_enc["input_ids"].shape == (3, 16)
    assert batch_enc["attention_mask"].shape == (3, 16)

    # Length audit
    audit = tokenizer.analyze_length_distribution(texts, max_length=5)
    assert audit["total_reports"] == 3
    assert audit["word_distribution"]["min"] >= 2
    assert "token_distribution" in audit
    assert audit["max_sequence_length_configured"] == 5


def test_class_weights_computation():
    """Verify class weight calculation handles severe imbalance and zero-count classes."""
    labels = ["CRITICAL", "CRITICAL", "HIGH", "NON-SIF"]
    weights = compute_class_weights(labels, DEFAULT_LABEL2ID, num_classes=5)

    assert isinstance(weights, torch.Tensor)
    assert weights.shape == (5,)
    # High-frequency CRITICAL should have lower weight than lower-frequency HIGH
    crit_idx = DEFAULT_LABEL2ID["CRITICAL"]
    high_idx = DEFAULT_LABEL2ID["HIGH"]
    assert weights[crit_idx] < weights[high_idx]


def test_dataset_item_generation():
    """Verify SIFTextDataset produces compliant tensors and label mappings."""
    mock_tok = TinyMockTokenizer(max_length=16)
    tokenizer = SafetyReportTokenizer(max_length=16, tokenizer=mock_tok)

    texts = ["Gas detector failed alarm test", "Worker wore safety harness"]
    labels = ["CRITICAL", "NON-SIF"]
    report_ids = ["REP-001", "REP-002"]

    dataset = SIFTextDataset(
        texts=texts,
        labels=labels,
        report_ids=report_ids,
        tokenizer=tokenizer,
        max_length=16,
    )

    assert len(dataset) == 2
    item0 = dataset[0]
    assert item0["report_id"] == "REP-001"
    assert item0["input_ids"].shape == (16,)
    assert item0["attention_mask"].shape == (16,)
    assert item0["label"] == DEFAULT_LABEL2ID["CRITICAL"]


def test_model_forward_and_loss(tiny_transformer_model):
    """Verify forward pass with standard and class-weighted loss."""
    model = tiny_transformer_model
    input_ids = torch.randint(0, 99, (2, 16), dtype=torch.long)
    attention_mask = torch.ones((2, 16), dtype=torch.long)
    labels = torch.tensor([0, 4], dtype=torch.long)

    # Standard loss
    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    assert "loss" in outputs
    assert outputs["loss"] is not None
    assert outputs["logits"].shape == (2, 5)
    assert outputs["probabilities"].shape == (2, 5)
    # Probabilities sum to 1.0
    probs_sum = outputs["probabilities"].sum(dim=-1)
    assert torch.allclose(probs_sum, torch.ones(2), atol=1e-5)

    # Class-weighted loss
    class_weights = torch.tensor([2.0, 1.5, 1.0, 0.5, 0.2], dtype=torch.float32)
    model.class_weights = class_weights
    weighted_outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    assert weighted_outputs["loss"] is not None


def test_inference_wrapper_and_schema(tiny_transformer_model):
    """Verify SIFTransformerClassifier returns valid SIFClassificationPrediction records."""
    mock_tok = TinyMockTokenizer(max_length=16)
    tokenizer = SafetyReportTokenizer(max_length=16, tokenizer=mock_tok)

    classifier = SIFTransformerClassifier(
        model=tiny_transformer_model,
        tokenizer=tokenizer,
        model_version="test-transformer-v1.0",
        device="cpu",
    )

    text = "High pressure line relief valve malfunctioned during production cycle"
    pred = classifier.predict(text)

    assert pred.task == "TASK-001"
    assert pred.model_version == "test-transformer-v1.0"
    assert pred.predicted_sif_potential in CANONICAL_SIF_CLASSES
    assert 0.0 <= pred.confidence <= 100.0
    assert pred.decision_scores.score_type == "uncalibrated_probability"
    assert len(pred.decision_scores.scores) == 5

    # Batch prediction
    batch_preds = classifier.predict_batch([text, "Minor slip without injury"])
    assert len(batch_preds) == 2


def test_model_save_and_reload_consistency(tiny_transformer_model, tmp_path):
    """Verify serializing and reloading transformer checkpoint produces identical predictions."""
    mock_tok = TinyMockTokenizer(max_length=16)
    tokenizer = SafetyReportTokenizer(max_length=16, tokenizer=mock_tok)

    classifier = SIFTransformerClassifier(
        model=tiny_transformer_model,
        tokenizer=tokenizer,
        model_version="test-reload-v1.0",
        device="cpu",
    )

    test_text = "Gas line unbolted without pressure bleedoff check"
    initial_pred = classifier.predict(test_text)

    # Save artifact
    save_dir = tmp_path / "saved_transformer"
    classifier.save(str(save_dir))

    assert (save_dir / "sift_model_meta.json").exists()
    assert (save_dir / "config.json").exists()

    # Reload using SIFTransformerModel.from_pretrained and custom tokenizer
    reloaded_model = SIFTransformerModel.from_pretrained(str(save_dir))
    reloaded_clf = SIFTransformerClassifier(
        model=reloaded_model,
        tokenizer=tokenizer,
        model_version="test-reload-v1.0",
        device="cpu",
    )
    reloaded_pred = reloaded_clf.predict(test_text)

    assert reloaded_pred.predicted_sif_potential == initial_pred.predicted_sif_potential
    assert abs(reloaded_pred.confidence - initial_pred.confidence) < 1e-3


def test_high_sif_recall_and_false_negative_audit():
    """Verify High-SIF recall computation and false negative categorization."""
    y_true = ["CRITICAL", "HIGH", "LOW", "NON-SIF"]
    y_pred = ["CRITICAL", "LOW", "LOW", "NON-SIF"]  # 1 false negative (HIGH -> LOW)
    report_ids = ["R1", "R2", "R3", "R4"]
    texts = [
        "Uncontrolled well blow out hazard observed",
        "Wire rope frayed beyond limit during crane lift operation",
        "Water puddle near doorway in office building",
        "Normal operation routine walk completed",
    ]

    metrics = compute_classification_metrics(y_true, y_pred)
    assert metrics.high_sif_support == 2
    assert metrics.high_sif_correct == 1
    assert metrics.high_sif_recall == 0.5

    report = FalseNegativeAnalyzer.analyze(report_ids, texts, y_true, y_pred)
    assert report.total_high_sif_false_negatives == 1
    assert "HIGH -> LOW" in report.high_sif_fn_breakdown
    assert report.false_negative_records[0].report_id == "R2"


def test_comparative_baseline_analysis():
    """Verify comparative reporting accurately identifies overlapping performance."""
    report_ids = ["R1", "R2", "R3", "R4"]
    texts = ["Text 1", "Text 2", "Text 3", "Text 4"]
    y_true = ["CRITICAL", "HIGH", "LOW", "NON-SIF"]
    y_classical = ["CRITICAL", "LOW", "LOW", "HIGH"]
    y_transformer = ["CRITICAL", "HIGH", "HIGH", "HIGH"]

    classical_m = {"accuracy": 0.5, "macro_f1": 0.4, "high_sif_recall": 0.5}
    transformer_m = {"accuracy": 0.5, "macro_f1": 0.45, "high_sif_recall": 1.0}

    report = generate_comparative_report(
        report_ids=report_ids,
        texts=texts,
        y_true=y_true,
        y_classical_pred=y_classical,
        y_transformer_pred=y_transformer,
        classical_metrics=classical_m,
        transformer_metrics=transformer_m,
        dataset_version="0.1.0",
        is_demo=True,
    )

    assert report.both_correct_count == 1  # R1
    assert report.transformer_only_count == 1  # R2
    assert report.classical_only_count == 1  # R3
    assert report.both_wrong_count == 1  # R4

    md = format_comparative_markdown(report)
    assert "Head-to-Head Performance Summary" in md
    assert "Comparative Prediction Overlap Matrix" in md
