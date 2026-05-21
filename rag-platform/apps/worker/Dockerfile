FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        poppler-utils \
        tesseract-ocr \
        tesseract-ocr-rus \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps/worker/app ./apps/worker/app

RUN pip install --no-cache-dir -e .

ENV PYTHONPATH=/app/packages:/app/apps/worker
CMD ["python", "-m", "app.worker"]
