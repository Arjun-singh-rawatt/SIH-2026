"""SIFT TASK-001 Feature Extraction Engine.

Wraps scikit-learn TfidfVectorizer to provide reproducible, leakage-free text feature representations
fitted strictly on training data partitions only.
"""

from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
import scipy.sparse as sp


class TfidfConfig(BaseModel):
    """Configuration hyperparameters for TF-IDF feature extraction."""
    ngram_range: Tuple[int, int] = (1, 2)
    sublinear_tf: bool = True
    min_df: int = 1
    max_features: Optional[int] = 10000
    strip_accents: str = "unicode"
    lowercase: bool = True


class TfidfFeatureExtractor:
    """TF-IDF Feature Extractor enforcing fit-on-train-only data protection."""

    def __init__(self, config: Optional[TfidfConfig] = None):
        self.config = config or TfidfConfig()
        self.vectorizer = TfidfVectorizer(
            ngram_range=self.config.ngram_range,
            sublinear_tf=self.config.sublinear_tf,
            min_df=self.config.min_df,
            max_features=self.config.max_features,
            strip_accents=self.config.strip_accents,
            lowercase=self.config.lowercase,
        )
        self.is_fitted = False

    def fit_transform_train(self, train_texts: List[str]) -> sp.csr_matrix:
        """Fit vocabulary on training texts and transform into TF-IDF sparse matrix.
        
        Args:
            train_texts: List of raw safety report narratives from TRAIN partition.
            
        Returns:
            Sparse matrix of TF-IDF feature vectors.
        """
        if not train_texts:
            raise ValueError("train_texts cannot be empty.")
        X_train = self.vectorizer.fit_transform(train_texts)
        self.is_fitted = True
        return X_train

    def transform(self, texts: List[str]) -> sp.csr_matrix:
        """Transform texts into TF-IDF sparse matrix using the pre-fitted training vocabulary.
        
        CRITICAL: Never fits on validation or test text to prevent data leakage.
        
        Args:
            texts: List of safety report narratives.
            
        Returns:
            Sparse matrix of TF-IDF feature vectors.
            
        Raises:
            RuntimeError: If called before fit_transform_train().
        """
        if not self.is_fitted:
            raise RuntimeError(
                "TfidfFeatureExtractor is not fitted. fit_transform_train() must be executed on training data first."
            )
        return self.vectorizer.transform(texts)

    @property
    def vocabulary_size(self) -> int:
        """Return the size of the learned training vocabulary."""
        return len(self.vectorizer.vocabulary_) if self.is_fitted else 0

    def get_feature_names(self) -> List[str]:
        """Return array of feature n-gram tokens."""
        return self.vectorizer.get_feature_names_out().tolist() if self.is_fitted else []
