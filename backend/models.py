from sqlalchemy import Column, Integer, String, Text
from .database import Base


class AppModel(Base):
    __tablename__ = "apps"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    nome_profissional = Column(String, nullable=False)
    profissao = Column(String, nullable=False)
    descricao = Column(Text, nullable=False)
    servicos_json = Column(Text, nullable=False)

    whatsapp = Column(String, nullable=False)
    instagram = Column(String, nullable=True)
    site = Column(String, nullable=True)
    endereco = Column(Text, nullable=True)

    cor_primaria = Column(String, default="#1E88E5")
    cor_secundaria = Column(String, default="#FFFFFF")
    logo_url = Column(String, nullable=True)

    # Portfólio (lista JSON de itens)
    portfolio_json = Column(Text, nullable=True)

    # Oferta principal (destaque comercial)
    oferta_titulo = Column(String, nullable=True)
    oferta_descricao = Column(Text, nullable=True)
    oferta_preco = Column(String, nullable=True)  # formato livre ex: "R$ 197", "a partir de R$ 80"

    # Depoimentos (lista JSON de {nome, texto})
    depoimentos_json = Column(Text, nullable=True)
