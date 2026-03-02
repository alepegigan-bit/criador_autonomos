from backend.database import Base, engine
from backend import models

print("Criando tabelas no banco apps.db ...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso.")