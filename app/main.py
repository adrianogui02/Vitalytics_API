from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.db.base import Base
from app.db.session import engine


def create_tables():
    print("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas criadas com sucesso.")


create_tables()


app = FastAPI(
    title="Vitalytics API",
    description="API para monitoramento de dados de saúde sobre a Síndrome Respiratória Aguda Grave (SRAG).",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Vitalytics de Monitoramento de Saúde"}
