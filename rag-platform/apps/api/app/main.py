from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import aink, documents, drawings, health, ism_vectors, llm, pilot, projects, search
from app.api.aink import requirements_router
from rag_storage.db import Base, get_engine
from rag_storage.config import get_settings
from rag_storage.qdrant_client import QdrantStore


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    Base.metadata.create_all(bind=get_engine())
    QdrantStore(settings).ensure_collections()
    yield


app = FastAPI(
    title="RAG Platform API",
    description="RAG-конвейер ПД/РД: инженерные токены, hybrid search, цитирование",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(projects.router, prefix="/projects", tags=["projects"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(drawings.router)
app.include_router(search.router, tags=["search"])
app.include_router(llm.router)
app.include_router(pilot.router)
app.include_router(aink.router)
app.include_router(requirements_router)
app.include_router(ism_vectors.router)
