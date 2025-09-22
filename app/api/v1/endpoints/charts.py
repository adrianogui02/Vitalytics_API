from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.db.session import SessionLocal
from app.crud import crud_srag
from app.schemas.chart import ChartResponse

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=ChartResponse)
def read_chart_data(
    start_date: date = Query(...,
                             description="Data de início no formato YYYY-MM-DD"),
    end_date: date = Query(...,
                           description="Data de fim no formato YYYY-MM-DD"),
    group_by: str = Query("day", enum=[
                          "day", "month", "state"], description="Agrupar por dia, mês ou estado"),
    state: Optional[str] = Query(
        None, description="Filtrar por UF do estado (ex: SP, RJ)", max_length=2),
    db: Session = Depends(get_db)
):
    """
    Fornece dados agregados para a visualização de gráficos de casos de SRAG.
    """
    chart_data = crud_srag.get_cases_grouped_by_time_and_region(
        db=db,
        start_date=start_date,
        end_date=end_date,
        group_by=group_by,
        state=state
    )

    return {
        "filter_options": {
            "start_date": start_date,
            "end_date": end_date,
            "group_by": group_by,
            "state": state
        },
        "data": chart_data
    }
