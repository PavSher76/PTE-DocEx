"""Отчёты по пакету ИСМ: JSON и PDF."""

from __future__ import annotations

import io
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.ism.models import (
    IsmDocument,
    IsmInterface,
    IsmProcessingError,
    IsmProcessingJob,
    IsmRagToken,
    IsmRequirement,
    IsmUploadBatch,
)


def build_batch_report(db: Session, batch_id: str) -> dict[str, Any]:
    batch = db.get(IsmUploadBatch, batch_id)
    if not batch:
        return {"error": "batch_not_found"}

    documents = list(db.query(IsmDocument).filter(IsmDocument.batch_id == batch_id).all())
    doc_ids = [d.id for d in documents]
    jobs = list(db.query(IsmProcessingJob).filter(IsmProcessingJob.batch_id == batch_id).all())
    interfaces = list(db.query(IsmInterface).filter(IsmInterface.batch_id == batch_id).all())
    errors = list(
        db.query(IsmProcessingError)
        .filter(IsmProcessingError.document_id.in_(doc_ids))
        .all()
        if doc_ids
        else []
    )

    by_status: dict[str, int] = {}
    for j in jobs:
        by_status[j.status] = by_status.get(j.status, 0) + 1

    review_pending = sum(1 for d in documents if d.review_status == "pending")
    review_approved = sum(1 for d in documents if d.review_status == "approved")
    review_rejected = sum(1 for d in documents if d.review_status == "rejected")

    tokens_total = 0
    if doc_ids:
        tokens_total = (
            db.query(IsmRagToken).filter(IsmRagToken.document_id.in_(doc_ids)).count()
        )

    report: dict[str, Any] = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "batch": {
            "id": batch.id,
            "title": batch.title,
            "project_cipher": batch.project_cipher,
            "status": batch.status,
            "ai_pipeline_status": batch.ai_pipeline_status,
            "created_at": batch.created_at.isoformat() if batch.created_at else None,
        },
        "summary": {
            "documents_total": len(documents),
            "jobs_by_status": by_status,
            "tokens_total": tokens_total,
            "interfaces_total": len(interfaces),
            "errors_total": len(errors),
            "review_pending": review_pending,
            "review_approved": review_approved,
            "review_rejected": review_rejected,
        },
        "ai_pipeline": batch.ai_pipeline_json or {},
        "documents": [
            {
                "id": d.id,
                "code": d.code,
                "title": d.title,
                "document_type": d.document_type,
                "revision": d.revision,
                "review_status": d.review_status,
                "review_notes": d.review_notes,
                "ai_classification": d.ai_classification,
                "requirements_count": db.query(IsmRequirement)
                .filter(IsmRequirement.document_id == d.id)
                .count(),
            }
            for d in documents
        ],
        "interfaces": [
            {
                "id": i.id,
                "source_document_id": i.source_document_id,
                "target_document_id": i.target_document_id,
                "link_type": i.link_type,
                "confidence": i.confidence,
                "reference_text": (i.reference_text or "")[:500],
            }
            for i in interfaces
        ],
        "errors": [
            {
                "document_id": e.document_id,
                "error_type": e.error_type,
                "message": e.message,
            }
            for e in errors
        ],
    }
    batch.report_json = report
    db.commit()
    return report


def render_batch_report_pdf(report: dict[str, Any]) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=14)
    batch = report.get("batch") or {}
    pdf.cell(0, 10, f"ISM Batch Report: {batch.get('title', batch.get('id', ''))}", ln=True)
    pdf.set_font("Helvetica", size=10)
    summary = report.get("summary") or {}
    pdf.cell(0, 8, f"Documents: {summary.get('documents_total', 0)}", ln=True)
    pdf.cell(0, 8, f"Tokens: {summary.get('tokens_total', 0)}", ln=True)
    pdf.cell(0, 8, f"Interfaces: {summary.get('interfaces_total', 0)}", ln=True)
    pdf.cell(0, 8, f"Review pending: {summary.get('review_pending', 0)}", ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 8, "Documents", ln=True)
    pdf.set_font("Helvetica", size=9)
    for doc in report.get("documents") or []:
        line = f"- [{doc.get('review_status')}] {doc.get('code') or '?'} | {doc.get('title', '')[:60]}"
        pdf.multi_cell(0, 6, _latin1_safe(line))

    pdf.add_page()
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 8, "AI duplicates / conflicts", ln=True)
    pdf.set_font("Helvetica", size=9)
    ai = report.get("ai_pipeline") or {}
    for dup in (ai.get("duplicates") or [])[:30]:
        pdf.multi_cell(0, 6, _latin1_safe(f"DUPE: {dup}"))
    for conf in (ai.get("conflicts") or [])[:30]:
        pdf.multi_cell(0, 6, _latin1_safe(f"CONF: {conf}"))

    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()


def _latin1_safe(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")
