from pydantic import BaseModel
from typing import List, Optional


class Servico(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: Optional[str] = None  # ex: "R$ 80", "a combinar"


class PortfolioItem(BaseModel):
    tipo: str  # ex: "imagem", "video"
    titulo: Optional[str] = None
    url: str


class Depoimento(BaseModel):
    nome: str
    texto: str


class AppBase(BaseModel):
    slug: str
    nome_profissional: str
    profissao: str
    descricao: str
    servicos: List[Servico]
    whatsapp: str
    instagram: Optional[str] = None
    site: Optional[str] = None
    endereco: Optional[str] = None
    cor_primaria: str = "#1E88E5"
    cor_secundaria: str = "#FFFFFF"
    logo_url: Optional[str] = None

    # Oferta
    oferta_titulo: Optional[str] = None
    oferta_descricao: Optional[str] = None
    oferta_preco: Optional[str] = None

    # Depoimentos (texto)
    depoimentos: Optional[List[Depoimento]] = None

    # Portfólio
    portfolio: Optional[List[PortfolioItem]] = None


class AppCreate(AppBase):
    pass


class AppUpdate(BaseModel):
    # slug não será editado aqui para simplificar
    nome_profissional: Optional[str] = None
    profissao: Optional[str] = None
    descricao: Optional[str] = None
    servicos: Optional[List[Servico]] = None
    whatsapp: Optional[str] = None
    instagram: Optional[str] = None
    site: Optional[str] = None
    endereco: Optional[str] = None
    cor_primaria: Optional[str] = None
    cor_secundaria: Optional[str] = None

    oferta_titulo: Optional[str] = None
    oferta_descricao: Optional[str] = None
    oferta_preco: Optional[str] = None

    depoimentos: Optional[List[Depoimento]] = None

    # Não vamos atualizar logo nem imagens de portfólio por aqui por enquanto


class AppOut(AppBase):
    id: int

    class Config:
        from_attributes = True  # pydantic v2