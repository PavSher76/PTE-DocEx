"""Шаблоны промптов для RAG-ответов."""

from rag_schemas.query import SearchHit

ANSWER_WITH_CITATIONS = """Ты — инженерный ассистент по проектной документации ПД/РД.
Отвечай ТОЛЬКО на основе приведённого контекста из загруженных документов проекта.
Если в контексте нет данных для ответа — напиши: «Не найдено в загруженных данных проекта.»
Не выдумывай нормы, номера документов и требования.
В конце перечисли использованные источники в формате [N] код_документа, стр. X.

Вопрос пользователя:
{query}

Контекст из инженерных токенов:
{context}
"""

EXTRACT_REQUIREMENTS = """Извлеки требования из фрагмента. Верни JSON-массив строк.
Только явные требования (должен, необходимо, требуется, предусмотреть).

Текст:
{text}
"""

SUMMARIZE_DOCUMENT = """Кратко опиши содержание фрагмента проектной документации (3–5 предложений).
Только факты из текста.

{text}
"""


def format_context_block(hits: list[SearchHit], max_chars: int = 12_000) -> str:
    parts: list[str] = []
    total = 0
    for i, hit in enumerate(hits, start=1):
        code = hit.document_code or hit.document_name or "—"
        page = hit.page_number if hit.page_number is not None else "—"
        sheet = hit.sheet_number or ""
        sheet_part = f", лист {sheet}" if sheet else ""
        block = (
            f"[{i}] {code}, стр. {page}{sheet_part}, тип={hit.element_type}\n"
            f"{hit.text[:800]}"
        )
        if total + len(block) > max_chars:
            break
        parts.append(block)
        total += len(block)
    return "\n\n".join(parts) if parts else "(контекст пуст)"
