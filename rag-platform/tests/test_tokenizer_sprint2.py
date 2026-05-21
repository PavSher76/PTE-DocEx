from uuid import uuid4

from rag_parsers.base import DocumentElementDTO
from rag_schemas.enums import ElementType
from rag_tokenizers.engineering import EngineeringTokenizer


def test_table_and_section_tokens():
    elements = [
        DocumentElementDTO(
            page_number=1,
            element_type="title",
            text="1 Общие положения",
            reading_order=1,
        ),
        DocumentElementDTO(
            page_number=2,
            element_type="table",
            text="ignored",
            table_markdown="| Параметр | Значение |\n| --- | --- |\n| Q | 10 |",
            reading_order=2,
        ),
        DocumentElementDTO(
            page_number=3,
            element_type="text",
            text="Система должна быть предусмотрена согласно СП 60.13330.",
            reading_order=3,
        ),
    ]
    tokens = EngineeringTokenizer().tokenize_elements(
        elements,
        project_id="PTE-25-450",
        document_id=uuid4(),
        version_id=uuid4(),
        source_uri="s3://bucket/doc.pdf",
        stage="PD",
        discipline="TX",
    )
    types = {t["element_type"] for t in tokens}
    assert ElementType.TABLE.value in types
    assert ElementType.REQUIREMENT.value in types
    assert any(t.get("parent_token_id") for t in tokens)
