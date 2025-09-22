from sqlalchemy import Column, Integer, String, Date, Boolean
from app.db.base import Base


class SragRecord(Base):
    __tablename__ = 'srag_records'

    id = Column(Integer, primary_key=True, index=True)
    dt_notific = Column(Date, index=True)
    sg_uf = Column(String, index=True)
    cs_sexo = Column(String)
    nu_idade_n = Column(Integer)
    uti = Column(Boolean, default=False)
    evolucao = Column(Integer, nullable=True)
    vacina_cov = Column(Boolean, default=False)
