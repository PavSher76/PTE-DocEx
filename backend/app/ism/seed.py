"""Начальное заполнение каталога процессов ИСМ."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ism.constants import DEFAULT_ISM_PROCESSES
from app.ism.models import IsmProcess


def seed_ism_processes(db: Session) -> int:
    created = 0
    for row in DEFAULT_ISM_PROCESSES:
        code = str(row["process_code"])
        exists = db.scalar(select(IsmProcess).where(IsmProcess.process_code == code))
        if exists:
            continue
        db.add(
            IsmProcess(
                process_code=code,
                process_name=str(row["process_name"]),
                owner=str(row.get("owner") or "ИСМ"),
                description=str(row.get("description") or ""),
                related_disciplines=list(row.get("related_disciplines") or []),
            )
        )
        created += 1
    if created:
        db.commit()
    return created
