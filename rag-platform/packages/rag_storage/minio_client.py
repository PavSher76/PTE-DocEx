from io import BytesIO
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import Config

from rag_storage.config import Settings


class MinioStorage:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = boto3.client(
            "s3",
            endpoint_url=self._endpoint_url(),
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            region_name=settings.minio_region,
            config=Config(signature_version="s3v4"),
        )
        self._ensure_bucket()

    def _endpoint_url(self) -> str:
        scheme = "https" if self._settings.minio_secure else "http"
        return f"{scheme}://{self._settings.minio_endpoint}"

    def _ensure_bucket(self) -> None:
        bucket = self._settings.minio_bucket
        try:
            self._client.head_bucket(Bucket=bucket)
        except Exception:
            self._client.create_bucket(Bucket=bucket)

    def upload_bytes(
        self,
        data: bytes,
        *,
        project_id: str,
        filename: str,
        content_type: str,
    ) -> str:
        key = f"{project_id}/{uuid4().hex}/{Path(filename).name}"
        self._client.put_object(
            Bucket=self._settings.minio_bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"s3://{self._settings.minio_bucket}/{key}"

    def upload_file_path(self, path: Path, *, project_id: str, content_type: str) -> str:
        return self.upload_bytes(
            path.read_bytes(),
            project_id=project_id,
            filename=path.name,
            content_type=content_type,
        )

    def download_bytes(self, storage_uri: str) -> bytes:
        bucket, key = self._parse_uri(storage_uri)
        buffer = BytesIO()
        self._client.download_fileobj(bucket, key, buffer)
        return buffer.getvalue()

    def upload_page_image(
        self,
        data: bytes,
        *,
        project_id: str,
        document_id,
        version_id,
        page_number: int,
    ) -> str:
        key = f"{project_id}/pages/{document_id}/{version_id}/page-{page_number:04d}.png"
        self._client.put_object(
            Bucket=self._settings.minio_bucket,
            Key=key,
            Body=data,
            ContentType="image/png",
        )
        return f"s3://{self._settings.minio_bucket}/{key}"

    def generate_presigned_url(self, storage_uri: str, *, expires_in: int = 3600) -> str:
        bucket, key = self._parse_uri(storage_uri)
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def delete_uri(self, storage_uri: str) -> None:
        try:
            bucket, key = self._parse_uri(storage_uri)
            self._client.delete_object(Bucket=bucket, Key=key)
        except Exception:
            pass

    def _parse_uri(self, storage_uri: str) -> tuple[str, str]:
        if not storage_uri.startswith("s3://"):
            raise ValueError(f"Неподдерживаемый URI: {storage_uri}")
        path = storage_uri.removeprefix("s3://")
        bucket, _, key = path.partition("/")
        return bucket, key
