from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import correspondence, documents, project_context
from app.config import get_settings
from app.database import Base, engine, migrate_sqlite_project_profiles_cipher
from app.schemas import HealthResponse

settings = get_settings()
settings.storage_dir.mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)
migrate_sqlite_project_profiles_cipher()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", app=settings.app_name)


app.include_router(correspondence.router, prefix=settings.api_prefix)
app.include_router(documents.router, prefix=settings.api_prefix)
app.include_router(project_context.router, prefix=settings.api_prefix)
