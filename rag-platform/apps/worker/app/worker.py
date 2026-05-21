"""RQ worker: python -m app.worker"""

import os
import sys

from redis import Redis
from rq import Worker

# PYTHONPATH: packages + apps/worker
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PACKAGES = os.path.join(ROOT, "packages")
WORKER_APP = os.path.join(ROOT, "apps", "worker")
for path in (PACKAGES, WORKER_APP):
    if path not in sys.path:
        sys.path.insert(0, path)

from rag_pipeline.logging_utils import configure_pipeline_logging  # noqa: E402
from rag_storage.config import get_settings  # noqa: E402


def main() -> None:
    configure_pipeline_logging()
    settings = get_settings()
    redis = Redis.from_url(settings.redis_url)
    worker = Worker(["ingest"], connection=redis)
    worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()
