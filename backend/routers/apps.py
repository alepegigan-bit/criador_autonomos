from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
import json
import os
import uuid

from .. import models, schemas
from ..database import SessionLocal

router = APIRouter(prefix="/api/apps", tags=["apps"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # .../backend
UPLOAD_DIR = os.path.join(os.path.dirname(BASE_DIR), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Extensões de imagem aceitas
EXTENSOES_SUPORTADAS = [".jpg", ".jpeg", ".png", ".gif", ".webp", ".jfif"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.AppOut)
async def create_app(
    slug: str = Form(...),
    nome_profissional: str = Form(...),
    profissao: str = Form(...),
    descricao: str = Form(...),
    servicos_json: str = Form(...),
    whatsapp: str = Form(...),
    instagram: str | None = Form(None),
    site: str | None = Form(None),
    endereco: str | None = Form(None),
    cor_primaria: str = Form("#1E88E5"),
    cor_secundaria: str = Form("#FFFFFF"),
    # Logo
    logo_file: UploadFile | None = File(None),
    # Portfólio (imagens)
    portfolio1: UploadFile | None = File(None),
    portfolio2: UploadFile | None = File(None),
    portfolio3: UploadFile | None = File(None),
    # Oferta principal
    oferta_titulo: str | None = Form(None),
    oferta_descricao: str | None = Form(None),
    oferta_preco: str | None = Form(None),
    # Depoimentos (como JSON string)
    depoimentos_json: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # Verifica slug único
    existing = db.query(models.AppModel).filter(models.AppModel.slug == slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug já em uso, escolha outro nome.")

    # Converte serviços de JSON string para lista
    try:
        servicos_list = json.loads(servicos_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato de serviços inválido.")

    # Converte depoimentos de JSON string para lista (se vier)
    depoimentos_list = None
    if depoimentos_json:
        try:
            depoimentos_list = json.loads(depoimentos_json)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Formato de depoimentos inválido.")

    # Salvar logo (se enviada)
    logo_url = None
    if logo_file is not None:
        ext = os.path.splitext(logo_file.filename)[1].lower()
        if ext not in EXTENSOES_SUPORTADAS:
            raise HTTPException(status_code=400, detail="Formato de imagem não suportado para logo.")
        filename = f"logo_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await logo_file.read())
        logo_url = f"/static/uploads/{filename}"

    # Salvar fotos de portfólio (se enviadas)
    portfolio_files = [portfolio1, portfolio2, portfolio3]
    portfolio_items = []
    for idx, pf in enumerate(portfolio_files, start=1):
        if pf is None:
            continue
        if not pf.filename:
            continue
        ext = os.path.splitext(pf.filename)[1].lower()
        if ext not in EXTENSOES_SUPORTADAS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de imagem não suportado na foto {idx}.",
            )
        filename = f"portfolio_{idx}_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await pf.read())
        portfolio_items.append(
            {
                "tipo": "imagem",
                "titulo": f"Foto {idx}",
                "url": f"/static/uploads/{filename}",
            }
        )

    servicos_json_str = json.dumps(servicos_list, ensure_ascii=False)
    portfolio_json_str = json.dumps(portfolio_items, ensure_ascii=False) if portfolio_items else None
    depoimentos_json_str = json.dumps(depoimentos_list, ensure_ascii=False) if depoimentos_list else None

    db_app = models.AppModel(
        slug=slug,
        nome_profissional=nome_profissional,
        profissao=profissao,
        descricao=descricao,
        servicos_json=servicos_json_str,
        whatsapp=whatsapp,
        instagram=instagram,
        site=site,
        endereco=endereco,
        cor_primaria=cor_primaria,
        cor_secundaria=cor_secundaria,
        logo_url=logo_url,
        portfolio_json=portfolio_json_str,
        oferta_titulo=oferta_titulo,
        oferta_descricao=oferta_descricao,
        oferta_preco=oferta_preco,
        depoimentos_json=depoimentos_json_str,
    )
    db.add(db_app)
    db.commit()
    db.refresh(db_app)

    servicos = json.loads(db_app.servicos_json)
    portfolio = json.loads(db_app.portfolio_json) if db_app.portfolio_json else None
    depoimentos = json.loads(db_app.depoimentos_json) if db_app.depoimentos_json else None

    return schemas.AppOut(
        id=db_app.id,
        slug=db_app.slug,
        nome_profissional=db_app.nome_profissional,
        profissao=db_app.profissao,
        descricao=db_app.descricao,
        servicos=servicos,
        whatsapp=db_app.whatsapp,
        instagram=db_app.instagram,
        site=db_app.site,
        endereco=db_app.endereco,
        cor_primaria=db_app.cor_primaria,
        cor_secundaria=db_app.cor_secundaria,
        logo_url=db_app.logo_url,
        portfolio=portfolio,
        oferta_titulo=db_app.oferta_titulo,
        oferta_descricao=db_app.oferta_descricao,
        oferta_preco=db_app.oferta_preco,
        depoimentos=depoimentos,
    )


@router.get("/{slug}", response_model=schemas.AppOut)
def get_app(slug: str, db: Session = Depends(get_db)):
    db_app = db.query(models.AppModel).filter(models.AppModel.slug == slug).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="App não encontrado.")

    servicos = json.loads(db_app.servicos_json)
    portfolio = json.loads(db_app.portfolio_json) if db_app.portfolio_json else None
    depoimentos = json.loads(db_app.depoimentos_json) if db_app.depoimentos_json else None

    return schemas.AppOut(
        id=db_app.id,
        slug=db_app.slug,
        nome_profissional=db_app.nome_profissional,
        profissao=db_app.profissao,
        descricao=db_app.descricao,
        servicos=servicos,
        whatsapp=db_app.whatsapp,
        instagram=db_app.instagram,
        site=db_app.site,
        endereco=db_app.endereco,
        cor_primaria=db_app.cor_primaria,
        cor_secundaria=db_app.cor_secundaria,
        logo_url=db_app.logo_url,
        portfolio=portfolio,
        oferta_titulo=db_app.oferta_titulo,
        oferta_descricao=db_app.oferta_descricao,
        oferta_preco

