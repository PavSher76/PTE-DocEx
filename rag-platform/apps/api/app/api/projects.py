from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from rag_schemas.project import ProjectCreate, ProjectRead
from rag_storage.db import get_db_session
from rag_storage.repositories.project import ProjectRepository

router = APIRouter()


def get_db():
    yield from get_db_session()


@router.post("", response_model=ProjectRead, status_code=201)
def create_project(body: ProjectCreate, db: Session = Depends(get_db)) -> ProjectRead:
    repo = ProjectRepository(db)
    if repo.get_by_project_id(body.project_id):
        raise HTTPException(status_code=409, detail="Проект с таким project_id уже существует.")
    row = repo.create(body.project_id, body.name, body.description)
    return ProjectRead.model_validate(row)


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)) -> list[ProjectRead]:
    return [ProjectRead.model_validate(p) for p in ProjectRepository(db).list_all()]
