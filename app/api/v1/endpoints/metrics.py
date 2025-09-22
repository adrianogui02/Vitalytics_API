from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.session import SessionLocal
from app.schemas.metric import MetricResponse
from app.services import srag_service

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[MetricResponse])
def read_metrics(db: Session = Depends(get_db)):
    """
    Retorna uma lista de métricas de saúde, incluindo a projeção anual de casos.
    """
    metrics = srag_service.calculate_all_metrics(db=db)
    return metrics
