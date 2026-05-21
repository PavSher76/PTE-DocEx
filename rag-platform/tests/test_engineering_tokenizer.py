from uuid import uuid4

from rag_parsers.base import DocumentElementDTO
from rag_schemas.enums import ElementType
from rag_tokenizers.engineering import EngineeringTokenizer


def test_requirement_detection():
    elements = [
        DocumentElementDTO(
            page_number=1,
            element_type="text",
            text="Система вентиляции должна быть предусмотрена согласно СП 60.13330.",
            reading_order=1,
        )
    ]
    tokens = EngineeringTokenizer().tokenize_elements(
        elements,
        project_id="PTE-25-450",
        document_id=uuid4(),
        version_id=uuid4(),
        source_uri="s3://test/doc.pdf",
    )
    assert len(tokens) == 1
    assert tokens[0]["element_type"] == ElementType.REQUIREMENT.value
    assert "СП" in "".join(tokens[0]["ntd_refs"])
