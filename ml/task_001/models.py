"""SIFT TASK-001 Classical Machine Learning Models.

Implements Logistic Regression and Linear Support Vector Machines with standardized
prediction interfaces, decision function extraction, and class-weighting options.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import scipy.sparse as sp
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC


class BaseSIFModel(ABC):
    """Abstract base class for SIFT classification models."""

    def __init__(self, name: str, random_seed: int = 42):
        self.name = name
        self.random_seed = random_seed
        self.classes_: np.ndarray = np.array([])
        self.is_trained = False

    @abstractmethod
    def fit(self, X: sp.csr_matrix, y: List[str]):
        """Fit model parameters on training feature matrix and labels."""
        pass

    @abstractmethod
    def predict(self, X: sp.csr_matrix) -> List[str]:
        """Predict categorical labels for feature matrix."""
        pass

    @abstractmethod
    def predict_scores(self, X: sp.csr_matrix) -> Tuple[List[Dict[str, float]], str]:
        """Compute decision function scores or probabilities per class.
        
        Returns:
            Tuple of (list of score dicts {class_name: score}, score_type string).
        """
        pass

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        """Return dictionary of model hyperparameters."""
        pass


class LogisticRegressionSIFClassifier(BaseSIFModel):
    """Multinomial / One-vs-Rest Logistic Regression classifier."""

    def __init__(
        self,
        C: float = 1.0,
        class_weight: Optional[str] = None,
        max_iter: int = 1000,
        random_seed: int = 42,
    ):
        super().__init__(name=f"LogisticRegression(class_weight={class_weight}, C={C})", random_seed=random_seed)
        self.C = C
        self.class_weight = class_weight
        self.max_iter = max_iter
        self.clf = LogisticRegression(
            C=self.C,
            class_weight=self.class_weight,
            max_iter=self.max_iter,
            random_state=self.random_seed,
            solver="lbfgs",
        )

    def fit(self, X: sp.csr_matrix, y: List[str]):
        self.clf.fit(X, y)
        self.classes_ = self.clf.classes_
        self.is_trained = True
        return self

    def predict(self, X: sp.csr_matrix) -> List[str]:
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() first.")
        preds = self.clf.predict(X)
        return [str(p) for p in preds]

    def predict_scores(self, X: sp.csr_matrix) -> Tuple[List[Dict[str, float]], str]:
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() first.")
        
        # In multi-class cases, predict_proba returns class probabilities
        probs = self.clf.predict_proba(X)
        score_list: List[Dict[str, float]] = []
        for row in probs:
            s_dict = {str(cls_name): round(float(p), 4) for cls_name, p in zip(self.classes_, row)}
            score_list.append(s_dict)
        return score_list, "uncalibrated_probability"

    def get_params(self) -> Dict[str, Any]:
        return {
            "model_type": "LogisticRegression",
            "C": self.C,
            "class_weight": self.class_weight,
            "max_iter": self.max_iter,
            "random_seed": self.random_seed,
            "solver": "lbfgs",
        }


class LinearSVMSIFClassifier(BaseSIFModel):
    """Linear Support Vector Classifier (LinearSVC)."""

    def __init__(
        self,
        C: float = 1.0,
        class_weight: Optional[str] = None,
        max_iter: int = 2000,
        random_seed: int = 42,
    ):
        super().__init__(name=f"LinearSVC(class_weight={class_weight}, C={C})", random_seed=random_seed)
        self.C = C
        self.class_weight = class_weight
        self.max_iter = max_iter
        self.clf = LinearSVC(
            C=self.C,
            class_weight=self.class_weight,
            max_iter=self.max_iter,
            random_state=self.random_seed,
            dual="auto",
        )

    def fit(self, X: sp.csr_matrix, y: List[str]):
        self.clf.fit(X, y)
        self.classes_ = self.clf.classes_
        self.is_trained = True
        return self

    def predict(self, X: sp.csr_matrix) -> List[str]:
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() first.")
        preds = self.clf.predict(X)
        return [str(p) for p in preds]

    def predict_scores(self, X: sp.csr_matrix) -> Tuple[List[Dict[str, float]], str]:
        if not self.is_trained:
            raise RuntimeError("Model is not trained. Call fit() first.")
        
        # Decision function margins
        df = self.clf.decision_function(X)
        score_list: List[Dict[str, float]] = []
        
        if len(self.classes_) == 2 and df.ndim == 1:
            # Binary classification shape (n_samples,)
            for val in df:
                score_list.append({
                    str(self.classes_[0]): round(float(-val), 4),
                    str(self.classes_[1]): round(float(val), 4),
                })
        else:
            for row in df:
                s_dict = {str(cls_name): round(float(score), 4) for cls_name, score in zip(self.classes_, row)}
                score_list.append(s_dict)
                
        return score_list, "decision_score"

    def get_params(self) -> Dict[str, Any]:
        return {
            "model_type": "LinearSVC",
            "C": self.C,
            "class_weight": self.class_weight,
            "max_iter": self.max_iter,
            "random_seed": self.random_seed,
            "dual": "auto",
        }


def build_candidate_models(random_seed: int = 42) -> Dict[str, BaseSIFModel]:
    """Factory creating candidate models for baseline validation comparison."""
    return {
        "lr_standard": LogisticRegressionSIFClassifier(C=1.0, class_weight=None, random_seed=random_seed),
        "lr_balanced": LogisticRegressionSIFClassifier(C=1.0, class_weight="balanced", random_seed=random_seed),
        "svm_standard": LinearSVMSIFClassifier(C=1.0, class_weight=None, random_seed=random_seed),
        "svm_balanced": LinearSVMSIFClassifier(C=1.0, class_weight="balanced", random_seed=random_seed),
    }
