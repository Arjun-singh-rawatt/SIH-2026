"""End-to-end integration tests connecting data splits, features, and model inference."""

import os
import pytest
from ml.common.dataset_loader import DatasetSplitLoader
from ml.task_001.features import TfidfFeatureExtractor
from ml.task_001.models import LogisticRegressionSIFClassifier
from ml.task_001.inference import SIFClassifier


def test_data_to_ml_pipeline_integration():
    """Verify that dataset splits from data/splits integrate seamlessly with ML feature extraction and inference."""
    demo_train_file = "data/splits/sift_demo_dataset_v0.1.0_train.jsonl"
    demo_test_file = "data/splits/sift_demo_dataset_v0.1.0_test.jsonl"
    
    if not os.path.exists(demo_train_file) or not os.path.exists(demo_test_file):
        pytest.skip("Demo dataset splits not found in data/splits")

    # 1. Load splits using ml.common.dataset_loader
    train_split = DatasetSplitLoader.load_split(demo_train_file, "TRAIN")
    test_split = DatasetSplitLoader.load_split(demo_test_file, "TEST")
    
    assert train_split.total_count > 0
    assert test_split.total_count > 0
    assert len(train_split.texts) > 0

    # 2. Extract features
    extractor = TfidfFeatureExtractor()
    X_train = extractor.fit_transform_train(train_split.texts)
    X_test = extractor.transform(test_split.texts)
    
    assert X_train.shape[0] == len(train_split.texts)
    assert X_test.shape[0] == len(test_split.texts)

    # 3. Train lightweight model
    model = LogisticRegressionSIFClassifier(random_seed=42)
    model.fit(X_train, train_split.labels)
    
    # 4. Wrap with SIFClassifier
    classifier = SIFClassifier(
        extractor=extractor,
        model=model,
        model_version="integration-test-v1",
    )
    
    # 5. Predict on test sample
    sample_text = test_split.texts[0]
    pred = classifier.predict(sample_text)
    assert pred.task == "TASK-001"
    assert pred.predicted_sif_potential in {"CRITICAL", "HIGH", "MEDIUM", "LOW", "NON-SIF"}
    assert pred.confidence is not None
