"""Граф связей (интерфейсов) между документами ИСМ."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ism.models import IsmDocument, IsmDocumentElement, IsmInterface, IsmProcess
from app.ism.schemas import IsmGraphEdge, IsmGraphNode, IsmGraphRead

_CROSS = re.compile(
    r"раздел\w*\s+(АР|КР|КЖ|ОВ|ВК|ЭО|ТХ|СС|ПОС|ГП|ПЗ|ИОС|АС|ТМ)|"
    r"(?:см\.?\s*|согласно\s+)(SOP[\-\w./]+|Форма[\s\w\-./]+)",
    re.IGNORECASE,
)


def build_interfaces_for_batch(db: Session, batch_id: str, documents: list[IsmDocument]) -> list[IsmInterface]:
    from sqlalchemy import delete

    db.execute(delete(IsmInterface).where(IsmInterface.batch_id == batch_id))
    by_code = {d.code.upper(): d for d in documents if d.code}
    by_disc: dict[str, list[IsmDocument]] = {}
    for d in documents:
        if d.discipline:
            by_disc.setdefault(d.discipline.upper(), []).append(d)

    links: list[IsmInterface] = []
    seen: set[str] = set()
    for doc in documents:
        text = doc.ai_summary or ""
        if doc.parse_raw_json and isinstance(doc.parse_raw_json, dict):
            text += "\n" + str(doc.parse_raw_json.get("full_text_preview", ""))
        for el in db.scalars(
            select(IsmDocumentElement).where(IsmDocumentElement.document_id == doc.id)
        ):
            text += "\n" + el.text

        for m in _CROSS.finditer(text):
            ref = m.group(1)
            if not ref:
                continue
            key = f"{doc.id}:{ref}:{m.start()}"
            if key in seen:
                continue
            seen.add(key)
            target: IsmDocument | None = None
            link_type = "references"
            if ref.upper() in by_code:
                target = by_code[ref.upper()]
                link_type = "references"
            elif len(ref) <= 4 and ref.upper() in by_disc:
                candidates = [x for x in by_disc[ref.upper()] if x.id != doc.id]
                target = candidates[0] if candidates else None
                link_type = "discipline_ref"

            links.append(
                IsmInterface(
                    batch_id=batch_id,
                    source_document_id=doc.id,
                    target_document_id=target.id if target else None,
                    link_type=link_type,
                    reference_text=text[max(0, m.start() - 60) : m.end() + 60].strip(),
                    target_discipline=ref.upper() if len(ref) <= 4 else None,
                    target_document_code=ref.upper() if len(ref) > 4 else None,
                    confidence=0.9 if target else 0.45,
                )
            )
    for link in links:
        db.add(link)
    db.commit()
    return links


def get_graph(
    db: Session,
    *,
    batch_id: str | None = None,
    process_id: str | None = None,
    document_type: str | None = None,
    owner: str | None = None,
    status: str | None = None,
) -> IsmGraphRead:
    q = select(IsmDocument)
    if batch_id:
        q = q.where(IsmDocument.batch_id == batch_id)
    if process_id:
        q = q.where(IsmDocument.ism_process_id == process_id)
    if document_type:
        q = q.where(IsmDocument.document_type == document_type)
    if owner:
        q = q.where(IsmDocument.owner == owner)
    if status:
        q = q.where(IsmDocument.status == status)
    documents = list(db.scalars(q).all())
    doc_ids = {d.id for d in documents}

    nodes: dict[str, IsmGraphNode] = {}
    for proc in db.scalars(select(IsmProcess)).all():
        nodes[f"process:{proc.id}"] = IsmGraphNode(
            id=f"process:{proc.id}",
            node_type="process",
            label=proc.process_name,
            meta={"process_code": proc.process_code},
        )

    for doc in documents:
        nodes[f"doc:{doc.id}"] = IsmGraphNode(
            id=f"doc:{doc.id}",
            node_type="document",
            label=doc.code or doc.title or doc.id[:8],
            meta={
                "document_type": doc.document_type,
                "title": doc.title,
                "revision": doc.revision,
                "status": doc.status,
            },
        )
        if doc.ism_process_id:
            nodes.setdefault(
                f"process:{doc.ism_process_id}",
                IsmGraphNode(
                    id=f"process:{doc.ism_process_id}",
                    node_type="process",
                    label="Процесс",
                ),
            )

    iface_q = select(IsmInterface)
    if batch_id:
        iface_q = iface_q.where(IsmInterface.batch_id == batch_id)
    interfaces = list(db.scalars(iface_q).all())

    edges: list[IsmGraphEdge] = []
    for iface in interfaces:
        if iface.source_document_id not in doc_ids:
            continue
        src = f"doc:{iface.source_document_id}"
        tgt = f"doc:{iface.target_document_id}" if iface.target_document_id else f"ref:{iface.id}"
        if iface.target_document_id and iface.target_document_id not in doc_ids:
            tgt = f"ref:{iface.id}"
            nodes[tgt] = IsmGraphNode(
                id=tgt,
                node_type="reference",
                label=iface.target_document_code or iface.target_discipline or "?",
            )
        edges.append(
            IsmGraphEdge(
                id=iface.id,
                source=src,
                target=tgt,
                link_type=iface.link_type,
                label=iface.reference_text[:80],
                confidence=iface.confidence,
            )
        )
        if doc := next((d for d in documents if d.id == iface.source_document_id), None):
            if doc.ism_process_id:
                edges.append(
                    IsmGraphEdge(
                        id=f"p-{iface.id}",
                        source=f"process:{doc.ism_process_id}",
                        target=src,
                        link_type="controls",
                        label="процесс",
                        confidence=1.0,
                    )
                )

    return IsmGraphRead(nodes=list(nodes.values()), edges=edges)
