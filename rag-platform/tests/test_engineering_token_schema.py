from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from rag_schemas.engineering_token import EngineeringTokenPayload
from rag_schemas.enums import ElementType


def test_engineering_token_payload_valid():
    payload = EngineeringTokenPayload(
        token_id=uuid4(),
        project_id="PTE-25-450",
        document_id=uuid4(),
        version_id=uuid4(),
        element_type=ElementType.REQUIREMENT,
        text="Объект должен соответствовать СП 60.13330.",
        source_uri="s3://documents/x.pdf",
        ntd_refs=["СП 60.13330"],
        created_at=datetime.now(timezone.utc),
    )
    assert payload.stage is None
    assert payload.ntd_refs


def test_bbox_requires_four_numbers():
    with pytest.raises(ValidationError):
        EngineeringTokenPayload(
            token_id=uuid4(),
            project_id="PTE-25-450",
            document_id=uuid4(),
            version_id=uuid4(),
            element_type=ElementType.TEXT,
            text="x",
            bbox=[1, 2, 3],
            source_uri="s3://x",
            created_at=datetime.now(timezone.utc),
        )
