from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrate_sqlite_project_profiles_cipher() -> None:
    """Существующие SQLite-БД создавались с колонкой slug; переименовываем в project_cipher."""

    if not str(engine.url).startswith("sqlite"):
        return
    with engine.begin() as conn:
        row = conn.execute(
            text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='project_profiles' LIMIT 1")
        ).fetchone()
        if row is None:
            return
        cols = conn.execute(text("PRAGMA table_info(project_profiles)")).fetchall()
        names = {c[1] for c in cols}
        if "slug" in names and "project_cipher" not in names:
            conn.execute(text("ALTER TABLE project_profiles RENAME COLUMN slug TO project_cipher"))


def migrate_sqlite_ism_columns() -> None:
    """Добавляет колонки review/AI/report в существующие SQLite-БД ИСМ."""

    if not str(engine.url).startswith("sqlite"):
        return
    alters: dict[str, list[tuple[str, str]]] = {
        "ism_documents": [
            ("ai_classification", "JSON"),
            ("review_status", "VARCHAR(32) DEFAULT 'pending'"),
            ("review_notes", "TEXT DEFAULT ''"),
            ("reviewed_at", "DATETIME"),
        ],
        "ism_upload_batches": [
            ("ai_pipeline_status", "VARCHAR(32) DEFAULT 'pending'"),
            ("ai_pipeline_json", "JSON"),
            ("report_json", "JSON"),
            ("reviewed_at", "DATETIME"),
        ],
    }
    with engine.begin() as conn:
        for table, columns in alters.items():
            row = conn.execute(
                text(f"SELECT 1 FROM sqlite_master WHERE type='table' AND name='{table}' LIMIT 1")
            ).fetchone()
            if row is None:
                continue
            existing = {c[1] for c in conn.execute(text(f"PRAGMA table_info({table})")).fetchall()}
            for col_name, col_def in columns:
                if col_name not in existing:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}"))
