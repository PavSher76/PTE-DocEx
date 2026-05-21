from app.config import Settings
from app.schema_mapper.registry import list_schema_versions, load_schema_version


def test_schema_v01_00_registered() -> None:
    versions = list_schema_versions()
    assert "v01_00" in versions


def test_load_schema_meta() -> None:
    settings = Settings(active_minstroy_design_assignment_schema_version="v01_00")
    info = load_schema_version(settings)
    assert info.schema_version == "01.00"
    assert info.type_code == "05.03"
    assert info.schema_path.exists()
    assert info.effective_from == "2025-07-09"
