import logging

from fastapi import FastAPI

from app.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

app = FastAPI(
    title="Design Assignment Parser",
    description="PDF «Задание на проектирование» → canonical JSON → Minstroy XML (XSD v01_00)",
    version="0.1.0",
)
app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "design-assignment-parser"}
