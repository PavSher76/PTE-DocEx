from rag_tokenizers.metadata import (
    detect_discipline,
    detect_document_code,
    detect_revision,
    detect_stage,
    extract_ntd_refs,
)


def test_detect_stage_and_discipline():
    text = "Стадия ПД. Раздел ПЗ-ТХ. Ревизия A."
    assert detect_stage(text) == "PD"
    assert detect_document_code(text) == "ПЗ-ТХ"
    assert detect_discipline("ПЗ-ТХ", text) == "TX"
    assert detect_revision(text) == "A"


def test_extract_ntd_refs():
    text = "В соответствии с СП 60.13330 и ГОСТ 21.110-2013."
    refs = extract_ntd_refs(text)
    assert any("СП" in ref for ref in refs)
    assert any("ГОСТ" in ref for ref in refs)
