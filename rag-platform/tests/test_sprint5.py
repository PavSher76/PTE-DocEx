from rag_evaluation.metrics import (
    answer_faithfulness_score,
    citation_correctness,
    precision_at_k,
    recall_at_k,
)
from rag_llm.guard import answer_declares_not_found, validate_citations
from rag_llm.prompts import format_context_block
from rag_schemas.query import SearchHit
from uuid import uuid4


def _hit(text: str = "тест") -> SearchHit:
    return SearchHit(
        token_id=uuid4(),
        score=0.9,
        text=text,
        document_id=uuid4(),
        document_name="doc.pdf",
        document_code="ПЗ-ТХ",
        page_number=1,
        element_type="text",
        source_uri="s3://x",
    )


def test_precision_at_k():
    assert precision_at_k(["a", "b", "c"], ["a", "c"], 3) == 2 / 3
    assert recall_at_k(["a", "b"], ["a", "c"], 5) == 0.5


def test_citation_correctness():
    assert citation_correctness("См. [1] и [2]", 2) == 1.0
    assert citation_correctness("См. [9]", 2) == 0.0


def test_guard_not_found():
    assert answer_declares_not_found("Не найдено в загруженных данных проекта.")
    assert validate_citations("Источник [1]", 3) == []


def test_faithfulness_empty_context():
    score = answer_faithfulness_score(
        "Не найдено в загруженных данных проекта.",
        declares_not_found=True,
        context_empty=True,
    )
    assert score == 1.0


def test_format_context_block():
    block = format_context_block([_hit("исходные данные")])
    assert "[1]" in block
    assert "исходные данные" in block


def test_evaluation_dataset_loads():
    from rag_evaluation import load_golden_dataset

    items = load_golden_dataset()
    assert len(items) >= 1
    assert items[0].query
