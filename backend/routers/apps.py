from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Body
from sqlalchemy.orm import Session
import json
import os
import uuid

from .. import models, schemas
from ..database import SessionLocal

router = APIRouter(prefix="/api/apps", tags=["apps"])

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
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
        # se não tiver arquivo selecionado, ignora
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

    servicos_json_str = json.dumps(servicos_list)
    portfolio_json_str = json.dumps(portfolio_items) if portfolio_items else None
    depoimentos_json_str = json.dumps(depoimentos_list) if depoimentos_list else None

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
        oferta_preco=db_app.oferta_preco,
        depoimentos=depoimentos,
    )


@router.put("/{slug}", response_model=schemas.AppOut)
def update_app(
    slug: str,
    app_update: schemas.AppUpdate = Body(...),
    db: Session = Depends(get_db),
):
    db_app = db.query(models.AppModel).filter(models.AppModel.slug == slug).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="App não encontrado.")

    data = app_update.model_dump(exclude_unset=True)

    # Atualiza campos simples
    for field in [
        "nome_profissional",
        "profissao",
        "descricao",
        "whatsapp",
        "instagram",
        "site",
        "endereco",
        "cor_primaria",
        "cor_secundaria",
        "oferta_titulo",
        "oferta_descricao",
        "oferta_preco",
    ]:
        if field in data and data[field] is not None:
            setattr(db_app, field, data[field])

    # Atualiza serviços
    if "servicos" in data and data["servicos"] is not None:
        servicos_list = [s.model_dump() for s in data["servicos"]]
        db_app.servicos_json = json.dumps(servicos_list)

    # Atualiza depoimentos em texto
    if "depoimentos" in data and data["depoimentos"] is not None:
        depo_list = [d.model_dump() for d in data["depoimentos"]]
        db_app.depoimentos_json = json.dumps(depo_list)

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


@router.post("/{slug}/imagens", response_model=schemas.AppOut)
async def update_images(
    slug: str,
    logo_file: UploadFile | None = File(None),
    portfolio1: UploadFile | None = File(None),
    portfolio2: UploadFile | None = File(None),
    portfolio3: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    db_app = db.query(models.AppModel).filter(models.AppModel.slug == slug).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="App não encontrado.")

    print("DEBUG update_images chamado para slug:", slug)

    # Atualiza logo se enviado
    if logo_file is not None:
        if logo_file.filename:  # só processa se tiver arquivo selecionado
            ext = os.path.splitext(logo_file.filename)[1].lower()
            print("DEBUG LOGO EXTENSÃO:", logo_file.filename, "->", ext)
            if ext not in EXTENSOES_SUPORTADAS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Formato de imagem não suportado para logo. Extensão recebida: {ext}",
                )
            filename = f"logo_{uuid.uuid4().hex}{ext}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(await logo_file.read())
            db_app.logo_url = f"/static/uploads/{filename}"

    # Atualiza portfólio se qualquer das novas imagens vier
    portfolio_files = [portfolio1, portfolio2, portfolio3]
    novos_portfolios = []

    for idx, pf in enumerate(portfolio_files, start=1):
        if pf is None:
            continue
        if not pf.filename:
            # input enviado sem arquivo, ignora
            continue
        ext = os.path.splitext(pf.filename)[1].lower()
        print("DEBUG PORTFOLIO EXTENSÃO:", pf.filename, "->", ext)
        if ext not in EXTENSOES_SUPORTADAS:
            raise HTTPException(
                status_code=400,
                detail=f"Formato de imagem não suportado na foto {idx}. Extensão recebida: {ext}",
            )
        filename = f"portfolio_{idx}_{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(await pf.read())
        novos_portfolios.append(
            {
                "tipo": "imagem",
                "titulo": f"Foto {idx}",
                "url": f"/static/uploads/{filename}",
            }
        )

    # Só substitui o portfólio se tiver pelo menos uma nova imagem válida
    if novos_portfolios:
        db_app.portfolio_json = json.dumps(novos_portfolios)

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