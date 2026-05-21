"""Тесты сборки проектного контекста комплекта."""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

from app.config import Settings
from app.schemas import (
    BundleContextExcerpt,
    BundleContextStructured,
    BundleDetailResponse,
    BundlePipelineFileStatus,
    BundleRagIngestInfo,
)
from app.services import bundle_project_context as bpc


def _settings(tmp: Path) -> Settings:
    return Settings(
        storage_dir=tmp / "storage",
        rag_enabled=True,
        rag_api_url="http://rag.test:8100",
    )


class BundleProjectContextTests(unittest.TestCase):
    def test_build_summary_includes_cipher_and_disciplines(self) -> None:
        structured = BundleContextStructured(
            batch_id="abc",
            project_cipher="3D01-TEST",
            rag_project_id="ANALIZ-abc",
            pipeline_status="indexed",
            pipeline_label="Индексация завершена",
            documents_indexed=2,
            documents_total=2,
            total_tokens=100,
            disciplines=["АР", "КР"],
            document_codes=["АР-01"],
        )
        excerpts = [
            BundleContextExcerpt(
                text="Назначение объекта — административное здание.",
                source="token",
                filename="doc.pdf",
            )
        ]
        summary = bpc._build_summary(structured, excerpts)
        self.assertIn("3D01-TEST", summary)
        self.assertIn("АР", summary)
        self.assertIn("Назначение объекта", summary)

    def test_merge_excerpts_deduplicates(self) -> None:
        docs = {
            "d1": bpc._DocAccumulator(
                document_id="d1",
                filename="a.pdf",
                job_status="indexed",
                rows=[
                    bpc._TokenRow(
                        text="Одинаковый фрагмент текста для проверки.",
                        element_type="section",
                        page_number=1,
                        discipline="АР",
                        document_code=None,
                        ntd_refs=[],
                    )
                ],
            )
        }
        search = [
            BundleContextExcerpt(
                text="Одинаковый фрагмент текста для проверки.",
                source="search",
                score=0.9,
            )
        ]
        merged = bpc._merge_excerpts(docs, search, max_excerpts=10)
        self.assertEqual(len(merged), 1)

    @patch("app.services.bundle_project_context.get_bundle_detail")
    @patch("app.services.bundle_project_context.httpx.Client")
    def test_build_persists_to_meta(
        self,
        client_cls: MagicMock,
        get_detail: MagicMock,
    ) -> None:
        with TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            settings = _settings(tmp)
            batch_id = "batch001"
            bundle_dir = settings.storage_dir / "document_bundles" / batch_id
            bundle_dir.mkdir(parents=True)
            meta_path = bundle_dir / "bundle_meta.json"
            meta_path.write_text(
                json.dumps(
                    {
                        "batch_id": batch_id,
                        "project_cipher": "CIPHER-1",
                        "rag_ingest": {"project_id": "ANALIZ-batch001"},
                    }
                ),
                encoding="utf-8",
            )

            get_detail.return_value = BundleDetailResponse(
                batch_id=batch_id,
                project_cipher="CIPHER-1",
                total_files=1,
                created_at=datetime.now(timezone.utc),
                overall_ukep_status="OK",
                bundle_manifest_crc32_hex="deadbeef",
                pipeline_status="indexed",
                pipeline_label="Индексация завершена",
                pipeline_files=[
                    BundlePipelineFileStatus(
                        filename="doc.pdf",
                        document_id="11111111-1111-1111-1111-111111111111",
                        job_status="indexed",
                        tokens_count=5,
                    )
                ],
                rag_ingest=BundleRagIngestInfo(
                    enabled=True,
                    status="queued",
                    project_id="ANALIZ-batch001",
                ),
            )

            mock_client = MagicMock()
            client_cls.return_value.__enter__.return_value = mock_client

            tokens_response = MagicMock()
            tokens_response.raise_for_status.return_value = None
            tokens_response.json.return_value = {
                "items": [
                    {
                        "text": "Раздел 1. Общие положения проектирования здания.",
                        "element_type": "section",
                        "page_number": 2,
                        "discipline": "АР",
                    }
                ]
            }

            search_response = MagicMock()
            search_response.raise_for_status.return_value = None
            search_response.json.return_value = {"hits": []}

            mock_client.get.return_value = tokens_response
            mock_client.post.return_value = search_response

            result = bpc.build_bundle_project_context(
                settings,
                batch_id,
                use_search=True,
                persist=True,
            )

            self.assertEqual(result.batch_id, batch_id)
            self.assertIn("CIPHER-1", result.summary)
            stored = json.loads(meta_path.read_text(encoding="utf-8"))
            self.assertIn("project_context", stored)
            self.assertEqual(stored["project_context"]["status"], result.status)


if __name__ == "__main__":
    unittest.main()
