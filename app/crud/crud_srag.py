from sqlalchemy import func, Date, extract
from sqlalchemy.orm import Session
from app.models.srag import SragRecord
from datetime import date
from typing import Optional, List, Tuple


def get_total_cases(db: Session) -> int:
    """Retorna o número total de casos de SRAG registrados."""
    return db.query(SragRecord).count()


def get_total_deaths(db: Session) -> int:
    """Retorna o número total de óbitos por SRAG."""
    return db.query(SragRecord).filter(SragRecord.evolucao == 2).count()


def get_total_uti_admissions(db: Session) -> int:
    """Retorna o número total de casos que necessitaram de internação em UTI."""
    return db.query(SragRecord).filter(SragRecord.uti == True).count()


def get_total_vaccinated(db: Session) -> int:
    """Retorna o número total de casos em que o paciente era vacinado contra COVID-19."""
    return db.query(SragRecord).filter(SragRecord.vacina_cov == True).count()


def get_cases_grouped_by_time_and_region(
    db: Session,
    start_date: date,
    end_date: date,
    group_by: str,
    state: Optional[str] = None
):
    """
    Busca casos de SRAG agrupados por período (dia/mês) ou por estado para os gráficos.
    """
    query = db.query(SragRecord).filter(
        SragRecord.dt_notific.between(start_date, end_date))

    if state:
        query = query.filter(SragRecord.sg_uf == state.upper())

    if group_by == 'day':
        group_field = func.date_trunc('day', SragRecord.dt_notific)
    elif group_by == 'month':
        group_field = func.date_trunc('month', SragRecord.dt_notific)
    elif group_by == 'state':
        group_field = SragRecord.sg_uf
    else:
        return []

    result = (
        query.with_entities(
            group_field.label('group'),
            func.count(SragRecord.id).label('count')
        )
        .group_by('group')
        .order_by('group')
        .all()
    )

    return [
        {"group": item.group.strftime(
            '%Y-%m-%d') if isinstance(item.group, date) else item.group, "count": item.count}
        for item in result
    ]


def get_all_yearly_counts(db: Session) -> List[dict]:
    """
    Busca a contagem de casos para cada ano disponível no banco de dados,
    ordenado por ano. Usado para a métrica de projeção anual.
    """
    result = db.query(
        extract('year', SragRecord.dt_notific).label('year'),
        func.count(SragRecord.id).label('count')
    ).group_by('year').order_by('year').all()

    return [{"year": int(item.year), "count": item.count} for item in result if item.year is not None]
