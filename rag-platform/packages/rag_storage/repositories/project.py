from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from rag_storage.models import Project


class ProjectRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(self, project_id: str, name: str, description: str = "") -> Project:
        row = Project(project_id=project_id, name=name, description=description)
        self._session.add(row)
        self._session.flush()
        return row

    def get_by_project_id(self, project_id: str) -> Project | None:
        return self._session.scalar(select(Project).where(Project.project_id == project_id))

    def get_by_uuid(self, id: UUID) -> Project | None:
        return self._session.get(Project, id)

    def list_all(self, limit: int = 100) -> list[Project]:
        return list(self._session.scalars(select(Project).limit(limit)))
