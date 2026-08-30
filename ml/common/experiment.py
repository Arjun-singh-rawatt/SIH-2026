"""SIFT Experiment Tracking & Lineage Logging.

Records reproducible JSON experiment metadata, library dependencies,
hyperparameter configurations, and generates Markdown metric reports.
"""

from datetime import datetime, timezone
import json
import os
import platform
import sys
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

import numpy as np
import sklearn

from ml.common.metrics import ClassificationMetrics
from ml.common.errors import ErrorAnalysisReport


class ExperimentRun(BaseModel):
    """Complete lineage and evaluation metadata for a single model training run."""
    experiment_id: str
    task: str = "TASK-001"
    dataset_version: str
    is_demo_dataset: bool = False
    model_type: str
    feature_type: str
    hyperparameters: Dict[str, Any]
    training_timestamp: str
    random_seed: int
    environment: Dict[str, str] = Field(default_factory=dict)
    validation_metrics: Optional[ClassificationMetrics] = None
    test_metrics: Optional[ClassificationMetrics] = None
    model_artifact_path: Optional[str] = None
    status: str = "COMPLETED"
    notes: Optional[str] = None


class ExperimentTracker:
    """Manages experiment directory creation, metadata persistence, and reporting."""

    @staticmethod
    def create_run_record(
        experiment_id: str,
        task: str,
        dataset_version: str,
        model_type: str,
        feature_type: str,
        hyperparameters: Dict[str, Any],
        random_seed: int,
        is_demo: bool = False,
        notes: Optional[str] = None,
    ) -> ExperimentRun:
        """Initialize an experiment run metadata record with environment details."""
        env = {
            "python_version": sys.version.split()[0],
            "sklearn_version": sklearn.__version__,
            "numpy_version": np.__version__,
            "platform": platform.platform(),
        }
        return ExperimentRun(
            experiment_id=experiment_id,
            task=task,
            dataset_version=dataset_version,
            is_demo_dataset=is_demo,
            model_type=model_type,
            feature_type=feature_type,
            hyperparameters=hyperparameters,
            training_timestamp=datetime.now(timezone.utc).isoformat(),
            random_seed=random_seed,
            environment=env,
            notes=notes,
        )

    @staticmethod
    def save_experiment_bundle(
        run: ExperimentRun,
        output_dir: str,
        val_metrics: Optional[ClassificationMetrics],
        test_metrics: Optional[ClassificationMetrics],
        error_report: Optional[ErrorAnalysisReport],
        predictions: Optional[List[Dict[str, Any]]] = None,
    ):
        """Write all experiment lineage artifacts to disk."""
        os.makedirs(output_dir, exist_ok=True)
        run.validation_metrics = val_metrics
        run.test_metrics = test_metrics

        # 1. experiment.json
        exp_file = os.path.join(output_dir, "experiment.json")
        with open(exp_file, "w", encoding="utf-8") as f:
            f.write(run.model_dump_json(indent=2))

        # 2. metrics.json
        if test_metrics:
            metrics_file = os.path.join(output_dir, "metrics.json")
            with open(metrics_file, "w", encoding="utf-8") as f:
                f.write(test_metrics.model_dump_json(indent=2))

        # 3. false_negatives.json
        if error_report:
            fn_file = os.path.join(output_dir, "false_negatives.json")
            with open(fn_file, "w", encoding="utf-8") as f:
                f.write(error_report.model_dump_json(indent=2))

        # 4. predictions.json
        if predictions:
            pred_file = os.path.join(output_dir, "predictions.json")
            with open(pred_file, "w", encoding="utf-8") as f:
                json.dump(predictions, f, indent=2)

        # 5. metrics.md
        md_file = os.path.join(output_dir, "metrics.md")
        md_content = ExperimentTracker._generate_markdown_report(run, val_metrics, test_metrics, error_report)
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md_content)

    @staticmethod
    def _generate_markdown_report(
        run: ExperimentRun,
        val_m: Optional[ClassificationMetrics],
        test_m: Optional[ClassificationMetrics],
        err_rep: Optional[ErrorAnalysisReport],
    ) -> str:
        """Render a clean Markdown experiment summary."""
        md = []
        md.append(f"# SIFT Experiment Report: `{run.experiment_id}`\n")
        md.append(f"**Task:** `{run.task}`  ")
        md.append(f"**Model Type:** `{run.model_type}`  ")
        md.append(f"**Dataset Version:** `{run.dataset_version}` {'*(DEMO DATASET - VALIDATION ONLY)*' if run.is_demo_dataset else ''}  ")
        md.append(f"**Timestamp:** `{run.training_timestamp}`  ")
        md.append(f"**Random Seed:** `{run.random_seed}`\n")
        md.append("---\n")

        if run.is_demo_dataset:
            md.append("> [!WARNING]\n> **DEMO DATASET NOTICE:** This model was evaluated against synthetic demo data. Performance numbers verify the pipeline infrastructure and do NOT represent production safety model performance.\n")

        md.append("## 1. Primary Evaluation Metrics\n")
        md.append("| Metric | Validation Split | Test Split (Out-of-Time) | Safety Target |")
        md.append("| :--- | :--- | :--- | :--- |")
        
        v_high = f"{val_m.high_sif_recall:.2%}" if val_m else "N/A"
        t_high = f"{test_m.high_sif_recall:.2%}" if test_m else "N/A"
        md.append(f"| **High-SIF Recall** | `{v_high}` | **`{t_high}`** | $\\ge 95.0\\%$ |")

        v_f1 = f"{val_m.macro_f1:.4f}" if val_m else "N/A"
        t_f1 = f"{test_m.macro_f1:.4f}" if test_m else "N/A"
        md.append(f"| **Macro F1** | `{v_f1}` | **`{t_f1}`** | $\\ge 0.88$ |")

        v_acc = f"{val_m.accuracy:.2%}" if val_m else "N/A"
        t_acc = f"{test_m.accuracy:.2%}" if test_m else "N/A"
        md.append(f"| **Accuracy** | `{v_acc}` | `{t_acc}` | Diagnostic |")

        v_wf1 = f"{val_m.weighted_f1:.4f}" if val_m else "N/A"
        t_wf1 = f"{test_m.weighted_f1:.4f}" if test_m else "N/A"
        md.append(f"| **Weighted F1** | `{v_wf1}` | `{t_wf1}` | Diagnostic |")
        md.append("\n---\n")

        if test_m and test_m.per_class_metrics:
            md.append("## 2. Test Split Per-Class Breakdown\n")
            md.append("| SIF Class | Support | Precision | Recall | F1 Score |")
            md.append("| :--- | :--- | :--- | :--- | :--- |")
            for c in test_m.per_class_metrics:
                md.append(f"| **{c.class_name}** | `{c.support}` | `{c.precision:.4f}` | `{c.recall:.4f}` | `{c.f1_score:.4f}` |")
            md.append("\n---\n")

        if err_rep:
            md.append("## 3. Safety-Critical False Negative Audit\n")
            md.append(f"- **Total Test Samples:** `{err_rep.total_samples}`\n")
            md.append(f"- **Total Misclassifications:** `{err_rep.total_misclassifications}`\n")
            md.append(f"- **High-SIF False Negatives (Critical/High $\\rightarrow$ Low/Non-SIF):** `{err_rep.total_high_sif_false_negatives}`\n")
            if err_rep.high_sif_fn_breakdown:
                md.append("\n### High-SIF Failure Transitions:\n")
                for k, v in err_rep.high_sif_fn_breakdown.items():
                    md.append(f"- `{k}`: **{v}** occurrences")

        return "\n".join(md)
