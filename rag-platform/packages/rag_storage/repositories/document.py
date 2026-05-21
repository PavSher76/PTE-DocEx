from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from rag_storage.models import Document, DocumentVersion, ProcessingJob, Project, SourceFile


class DocumentRepository:
    def __init__(self, session: Session):
        self._session = session

    def create_document_with_upload(
        self,
        *,
        project: Project,
        name: str,
        filename: str,
        content_type: str,
        file_type: str,
        size_bytes: int,
        storage_uri: str,
        document_code: str | None = None,
        stage: str | None = None,
        discipline: str | None = None,
        rag_collection: str | None = None,
    ) -> tuple[Document, DocumentVersion, SourceFile, ProcessingJob]:
        document = Document(
            project_uuid=project.id,
            name=name,
            document_code=document_code,
            stage=stage,
            discipline=discipline,
            rag_collection=rag_collection,
        )
        version = DocumentVersion(document=document, revision=None, status=None, is_current=True)
        source = SourceFile(
            version=version,
            filename=filename,
            content_type=content_type,
            file_type=file_type,
            size_bytes=size_bytes,
            storage_uri=storage_uri,
        )
        self._session.add_all([document, version, source])
        self._session.flush()
        job = ProcessingJob(
            document_id=document.id,
            version_id=version.id,
            status="uploaded",
        )
        self._session.add(job)
        self._session.flush()
        return document, version, source, job

    def get_document(self, document_id: UUID) -> Document | None:
        return self._session.get(Document, document_id)

    def get_job(self, job_id: UUID) -> ProcessingJob | None:
        return self._session.get(ProcessingJob, job_id)

    def get_latest_job_for_document(self, document_id: UUID) -> ProcessingJob | None:
        return self._session.scalar(
            select(ProcessingJob)
            .where(ProcessingJob.document_id == document_id)
            .order_by(ProcessingJob.created_at.desc())
            .limit(1)
        )

    def update_job_status(
        self,
        job: ProcessingJob,
        status: str,
        *,
        stage: str | None = None,
        error_message: str | None = None,
        rq_job_id: str | None = None,
    ) -> ProcessingJob:
        job.status = status
        if stage is not None:
            job.stage = stage
        if error_message is not None:
            job.error_message = error_message
        if rq_job_id is not None:
            job.rq_job_id = rq_job_id
        self._session.flush()
        return job

    def count_tokens_for_version(self, version_id: UUID) -> int:
        from rag_storage.models import EngineeringToken

        return int(
            self._session.scalar(
                select(func.count()).select_from(EngineeringToken).where(
                    EngineeringToken.version_id == version_id
                )
            )
            or 0
        )

    def new_job_id(self) -> UUID:
        return uuid4()
