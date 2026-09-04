"""Tests for SIFT TASK-001 TF-IDF Feature Extraction Engine (Leakage-Free Invariant)."""

import pytest
from ml.task_001.features import TfidfFeatureExtractor, TfidfConfig


def test_tfidf_fit_transform_train_only():
    """Verify TF-IDF fits vocabulary on training data and transforms test data without fitting."""
    train_texts = [
        "High pressure gas manifold leak 40 bar during valve maintenance.",
        "Scaffold worker observed at 8m elevation without harness tie-off.",
        "Minor oil weeping on pump skid drip tray.",
    ]
    test_texts = [
        "High pressure gas leak detected.",
        "New unseen terminology deepwater riser leak.",
    ]

    extractor = TfidfFeatureExtractor(TfidfConfig(ngram_range=(1, 2)))
    
    # 1. Transform before fit must raise error
    with pytest.raises(RuntimeError, match="TfidfFeatureExtractor is not fitted"):
        extractor.transform(test_texts)

    # 2. Fit on train
    X_train = extractor.fit_transform_train(train_texts)
    assert X_train.shape[0] == 3
    vocab_size = extractor.vocabulary_size
    assert vocab_size > 0

    # 3. Transform test
    X_test = extractor.transform(test_texts)
    assert X_test.shape[0] == 2
    assert X_test.shape[1] == X_train.shape[1]
    
    # Vocabulary size must not change after transforming test text (zero test vocabulary leakage)
    assert extractor.vocabulary_size == vocab_size
