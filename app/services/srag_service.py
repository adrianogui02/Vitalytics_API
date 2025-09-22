from sqlalchemy.orm import Session
from app.crud import crud_srag
from app.schemas.metric import Metric, ProjectionMetric
from typing import List, Union


def calculate_all_metrics(db: Session) -> List[Union[Metric, ProjectionMetric]]:
    metrics: List[Union[Metric, ProjectionMetric]] = []

    total_cases = crud_srag.get_total_cases(db)

    if total_cases == 0:
        return []

    # --- Métrica 1: Taxa de Mortalidade --------------------------------------
    total_deaths = crud_srag.get_total_deaths(db)
    mortality_rate = (total_deaths / total_cases) * 100
    metrics.append(Metric(
        name="Taxa de Mortalidade por SRAG",
        value=f"{mortality_rate:.2f}%",
        context=f"Calculada com base em {total_deaths} óbitos de um total de {total_cases} casos."
    ))

    # --- Métrica 2: Taxa de Admissão em UTI ----------------------------------
    uti_admissions = crud_srag.get_total_uti_admissions(db)
    uti_rate = (uti_admissions / total_cases) * 100
    metrics.append(Metric(
        name="Taxa de Admissão em UTI",
        value=f"{uti_rate:.2f}%",
        context=f"Percentual de casos que necessitaram de internação em UTI. ({uti_admissions} de {total_cases})"
    ))

    # --- Métrica 3: Taxa de Vacinação ----------------------------------------
    vaccinated = crud_srag.get_total_vaccinated(db)
    vaccination_rate = (vaccinated / total_cases) * 100
    metrics.append(Metric(
        name="Taxa de Vacinação (COVID)",
        value=f"{vaccination_rate:.2f}%",
        context=f"Percentual de pacientes com SRAG que receberam a vacina contra a COVID-19."
    ))

    # --- Métrica 4: Projeção de Crescimento Anual ----------------------------
    yearly_counts = crud_srag.get_all_yearly_counts(db)
    projection_data = []
    counts_by_year = {item['year']: item['count'] for item in yearly_counts}

    for item in yearly_counts:
        year = item['year']
        count = item['count']
        previous_year_count = counts_by_year.get(year - 1)

        percentage_change = None
        if previous_year_count is not None and previous_year_count > 0:
            change = ((count - previous_year_count) /
                      previous_year_count) * 100
            percentage_change = round(change, 2)

        projection_data.append({
            "year": year,
            "case_count": count,
            "percentage_change": percentage_change
        })

    metrics.append(ProjectionMetric(
        name="Variação Anual de Casos",
        context="Variação percentual no número de casos em relação ao ano anterior.",
        data=projection_data
    ))

    return metrics
