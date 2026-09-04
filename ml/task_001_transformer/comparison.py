"""SIFT Baseline vs Transformer Comparative Benchmark & Error Overlap Analyzer.

Compares classical TF-IDF (LR / SVM) against fine-tuned Transformer predictions
on the locked out-of-time test split to assess contextual language understanding gains.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ComparativeRecord(BaseModel):
    """Comparative analysis for a single test sample."""
    report_id: str
    raw_text: str
    actual_label: str
    classical_prediction: str
    transformer_prediction: str
    classical_correct: bool
    transformer_correct: bool
    category: str  # BOTH_CORRECT, CLASSICAL_ONLY, TRANSFORMER_ONLY, BOTH_WRONG


class ComparativeBenchmarkReport(BaseModel):
    """Aggregate benchmark comparison between classical baseline and transformer."""
    task: str = "TASK-001"
    dataset_version: str
    is_demo_dataset: bool
    test_sample_count: int
    classical_model_name: str
    transformer_model_name: str

    classical_accuracy: float
    classical_macro_f1: float
    classical_high_sif_recall: float

    transformer_accuracy: float
    transformer_macro_f1: float
    transformer_high_sif_recall: float

    both_correct_count: int
    classical_only_count: int
    transformer_only_count: int
    both_wrong_count: int

    records: List[ComparativeRecord] = Field(default_factory=list)


def generate_comparative_report(
    report_ids: List[str],
    texts: List[str],
    y_true: List[str],
    y_classical_pred: List[str],
    y_transformer_pred: List[str],
    classical_metrics: Dict[str, Any],
    transformer_metrics: Dict[str, Any],
    classical_model_name: str = "TF-IDF + LogisticRegression",
    transformer_model_name: str = "DistilBERT (distilbert-base-uncased)",
    dataset_version: str = "0.1.0",
    is_demo: bool = True,
) -> ComparativeBenchmarkReport:
    """Analyze overlap between classical baseline and transformer predictions."""
    total = len(y_true)
    both_correct = 0
    classical_only = 0
    transformer_only = 0
    both_wrong = 0
    records: List[ComparativeRecord] = []

    for i in range(total):
        r_id = report_ids[i] if i < len(report_ids) else f"TEST-{i}"
        txt = texts[i] if i < len(texts) else ""
        actual = y_true[i]
        c_pred = y_classical_pred[i]
        t_pred = y_transformer_pred[i]

        c_ok = (c_pred == actual)
        t_ok = (t_pred == actual)

        if c_ok and t_ok:
            cat = "BOTH_CORRECT"
            both_correct += 1
        elif c_ok and not t_ok:
            cat = "CLASSICAL_ONLY"
            classical_only += 1
        elif not c_ok and t_ok:
            cat = "TRANSFORMER_ONLY"
            transformer_only += 1
        else:
            cat = "BOTH_WRONG"
            both_wrong += 1

        records.append(ComparativeRecord(
            report_id=r_id,
            raw_text=(txt[:120] + "...") if len(txt) > 120 else txt,
            actual_label=actual,
            classical_prediction=c_pred,
            transformer_prediction=t_pred,
            classical_correct=c_ok,
            transformer_correct=t_ok,
            category=cat,
        ))

    return ComparativeBenchmarkReport(
        dataset_version=dataset_version,
        is_demo_dataset=is_demo,
        test_sample_count=total,
        classical_model_name=classical_model_name,
        transformer_model_name=transformer_model_name,
        classical_accuracy=classical_metrics.get("accuracy", 0.0),
        classical_macro_f1=classical_metrics.get("macro_f1", 0.0),
        classical_high_sif_recall=classical_metrics.get("high_sif_recall", 0.0),
        transformer_accuracy=transformer_metrics.get("accuracy", 0.0),
        transformer_macro_f1=transformer_metrics.get("macro_f1", 0.0),
        transformer_high_sif_recall=transformer_metrics.get("high_sif_recall", 0.0),
        both_correct_count=both_correct,
        classical_only_count=classical_only,
        transformer_only_count=transformer_only,
        both_wrong_count=both_wrong,
        records=records,
    )


def format_comparative_markdown(report: ComparativeBenchmarkReport) -> str:
    """Format comparative analysis as clean GitHub-style Markdown."""
    md = []
    md.append(f"# SIFT TASK-001 Benchmark Comparison: Classical Baseline vs Transformer\n")
    md.append(f"**Dataset Version:** `{report.dataset_version}` {'*(DEMO / PIPELINE VALIDATION ONLY)*' if report.is_demo_dataset else ''}  ")
    md.append(f"**Test Sample Count:** `{report.test_sample_count}` (Evaluated on identical locked test set)\n")

    if report.is_demo_dataset:
        md.append("> [!WARNING]\n> **DEMO DATASET NOTICE:** Evaluated against synthetic demo data. Numbers demonstrate end-to-end pipeline integrity and do NOT represent production statistical performance.\n")

    md.append("## 1. Head-to-Head Performance Summary\n")
    md.append("| Model Architecture | Accuracy | Macro F1 | HIGH-SIF Recall | Parameter Count |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    md.append(f"| **Classical ({report.classical_model_name})** | `{report.classical_accuracy:.2%}` | `{report.classical_macro_f1:.4f}` | **`{report.classical_high_sif_recall:.2%}`** | ~N-Gram Vocab |")
    md.append(f"| **Transformer ({report.transformer_model_name})** | `{report.transformer_accuracy:.2%}` | `{report.transformer_macro_f1:.4f}` | **`{report.transformer_high_sif_recall:.2%}`** | ~66.36M |")
    md.append("\n---\n")

    md.append("## 2. Comparative Prediction Overlap Matrix\n")
    md.append("| Category | Record Count | Percentage | Operational Interpretation |")
    md.append("| :--- | :--- | :--- | :--- |")
    n = report.test_sample_count or 1
    md.append(f"| **Both Correct** | `{report.both_correct_count}` | `{report.both_correct_count / n:.1%}` | High agreement across salient hazard vocabulary. |")
    md.append(f"| **Transformer Only** | `{report.transformer_only_count}` | `{report.transformer_only_count / n:.1%}` | Contextual syntax / passive phrasing captured. |")
    md.append(f"| **Classical Only** | `{report.classical_only_count}` | `{report.classical_only_count / n:.1%}` | Direct keyword match prioritized over subtle context. |")
    md.append(f"| **Both Wrong** | `{report.both_wrong_count}` | `{report.both_wrong_count / n:.1%}` | High ambiguity, missing context, or rare hazard terminology. |")
    md.append("\n---\n")

    if report.records:
        md.append("## 3. Sample-Level Case Comparisons\n")
        md.append("| Report ID | Actual Label | Classical Pred | Transformer Pred | Category | Narrative Excerpt |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
        for r in report.records:
            md.append(f"| `{r.report_id}` | `{r.actual_label}` | `{r.classical_prediction}` | `{r.transformer_prediction}` | `{r.category}` | {r.raw_text} |")

    return "\n".join(md)
