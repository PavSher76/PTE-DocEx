from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from rag_storage.models import EngineeringToken


class TokenRepository:
    def __init__(self, session: Session):
        self._session = session

    def bulk_create(self, tokens: list[EngineeringToken]) -> None:
        self._session.add_all(tokens)
        self._session.flush()

    def list_by_version(self, version_id: UUID, limit: int = 500, offset: int = 0) -> list[EngineeringToken]:
        return list(
            self._session.scalars(
                select(EngineeringToken)
                .where(EngineeringToken.version_id == version_id)
                .order_by(EngineeringToken.page_number, EngineeringToken.created_at)
                .offset(offset)
                .limit(limit)
            )
        )

    def delete_by_version(self, version_id: UUID) -> int:
        rows = list(
            self._session.scalars(select(EngineeringToken).where(EngineeringToken.version_id == version_id))
        )
        for row in rows:
            self._session.delete(row)
        self._session.flush()
        return len(rows)
