FROM python:3.12-slim

ARG HTTP_PROXY=
ARG HTTPS_PROXY=
ARG NO_PROXY=
# Set to 1 to skip apt (LibreOffice/OCR) when corporate proxy blocks deb.debian.org
ARG SKIP_APT_PACKAGES=0

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=120 \
    PIP_RETRIES=10 \
    HTTP_PROXY=$HTTP_PROXY \
    HTTPS_PROXY=$HTTPS_PROXY \
    NO_PROXY=$NO_PROXY \
    http_proxy=$HTTP_PROXY \
    https_proxy=$HTTPS_PROXY \
    no_proxy=$NO_PROXY

WORKDIR /app

COPY requirements.txt docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# pip runs at container start (entrypoint) so host/corporate DNS and proxy apply.
RUN if [ "$SKIP_APT_PACKAGES" != "1" ]; then \
      if [ -n "$HTTP_PROXY" ]; then \
        proxy="${HTTPS_PROXY:-$HTTP_PROXY}"; \
        printf '%s\n' \
          "Acquire::http::Proxy \"${HTTP_PROXY}\";" \
          "Acquire::https::Proxy \"${proxy}\";" \
          'Acquire::http::Timeout "120";' \
          'Acquire::https::Timeout "120";' \
          'Acquire::Retries "5";' \
          > /etc/apt/apt.conf.d/99proxy; \
      fi \
      && apt-get update \
      && apt-get install -y --no-install-recommends \
          libreoffice \
          poppler-utils \
          tesseract-ocr \
          tesseract-ocr-rus \
          tesseract-ocr-eng \
      && rm -rf /var/lib/apt/lists/*; \
    else \
      echo "SKIP_APT_PACKAGES=1: skipping LibreOffice/Tesseract (OCR/compare may be limited)"; \
    fi

COPY app ./app

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
