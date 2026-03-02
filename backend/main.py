import os
import json
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .database import SessionLocal
from . import models
from .routers import apps as apps_router

BASE_DIR = os.path.dirname(__file__)  # ...\criador_autonomos\backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # ...\criador_autonomos
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# /static aponta para a raiz do projeto, onde temos /static e /uploads
app.mount("/static", StaticFiles(directory=PROJECT_ROOT), name="static")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

app.include_router(apps_router.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/criar")
def criar_app_page(request: Request):
    return templates.TemplateResponse("criar.html", {"request": request})


@app.get("/editar/{slug}")
def editar_app_page(slug: str, request: Request):
    # A página de edição vai buscar os dados via JS na rota /api/apps/{slug}
    return templates.TemplateResponse("editar.html", {"request": request, "slug": slug})


@app.get("/app/{slug}")
def view_app(slug: str, request: Request, db: Session = Depends(get_db)):
    db_app = db.query(models.AppModel).filter(models.AppModel.slug == slug).first()
    if not db_app:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "mensagem": "App não encontrado."},
            status_code=404,
        )

    servicos = json.loads(db_app.servicos_json)
    portfolio = json.loads(db_app.portfolio_json) if db_app.portfolio_json else []
    depoimentos = json.loads(db_app.depoimentos_json) if db_app.depoimentos_json else []

    return templates.TemplateResponse(
        "app.html",
        {
            "request": request,
            "app": db_app,
            "servicos": servicos,
            "portfolio": portfolio,
            "depoimentos": depoimentos,
        },
    )