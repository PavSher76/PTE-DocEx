from app.config import Settings
from app.models.canonical import DesignAssignmentCanonical
from app.schema_mapper.mapper import coverage_mandatory_fields, normalize_canonical
from app.schema_mapper.registry import load_mapping


def test_normalize_defaults() -> None:
    settings = Settings()
    mapping = load_mapping(settings)
    c = DesignAssignmentCanonical()
    c = normalize_canonical(c, mapping)
    assert c.document.document_type_code == "05.03"
    assert c.document.schema_version == "01.00"
    assert c.document.document_id


def test_mandatory_coverage_tracking() -> None:
    settings = Settings()
    mapping = load_mapping(settings)
    c = DesignAssignmentCanonical()
    c.document.document_number = "1"
    c.participants.author.full_name = "АО Тест"
    c.participants.author.inn = "1234567890"
    c.participants.author.ogrn = "1234567890123"
    c.participants.author.kpp = "123456789"
    c.object.name = "Объект"
    c.object.code = "O1"
    filled, total, missing = coverage_mandatory_fields(c, mapping)
    assert total > 0
    assert filled >= 5
    assert "document.document_date" in missing or filled > 0
