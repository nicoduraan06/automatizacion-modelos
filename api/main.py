from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
import os

from api.upload import router as upload_router
from api.process import router as process_router
from api.download import router as download_router
from api.result import router as result_router

app = FastAPI(title="modelo303")


# 🔥 RUTA CORRECTA (SIN templates)
BASE_DIR = Path(os.getcwd())
FRONTEND_PATH = BASE_DIR / "frontend" / "index.html"


@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    if not FRONTEND_PATH.exists():
        return f"<h1>No se encuentra el frontend en:<br>{FRONTEND_PATH}</h1>"

    return FRONTEND_PATH.read_text(encoding="utf-8")


# ROUTERS
app.include_router(upload_router, prefix="/api")
app.include_router(process_router, prefix="/api")
app.include_router(download_router, prefix="/api")
app.include_router(result_router, prefix="/api")