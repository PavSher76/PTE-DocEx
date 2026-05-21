from rag_storage.collections import (
    RAG_COLLECTION_PROJECT_ANALYSIS,
    text_collection_for,
)
from rag_storage.config import Settings
from rag_storage.models import Document


def test_analysis_collection_routing():
    settings = Settings()
    doc = Document(name="x.pdf", rag_collection=RAG_COLLECTION_PROJECT_ANALYSIS)
    assert text_collection_for(doc, settings) == settings.qdrant_collection_project_analysis

    doc_default = Document(name="y.pdf", rag_collection=None)
    assert text_collection_for(doc_default, settings) == settings.qdrant_collection_text
