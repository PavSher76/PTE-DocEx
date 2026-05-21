"""Метрики retrieval и faithfulness (этап 13)."""

from rag_evaluation.dataset import GoldenQuestion, load_golden_dataset
from rag_evaluation.metrics import (
    RetrievalMetrics,
    answer_faithfulness_score,
    citation_correctness,
    compute_retrieval_metrics,
    precision_at_k,
)

__all__ = [
    "GoldenQuestion",
    "RetrievalMetrics",
    "answer_faithfulness_score",
    "citation_correctness",
    "compute_retrieval_metrics",
    "load_golden_dataset",
    "precision_at_k",
]
