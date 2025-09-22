from pydantic import BaseModel
from typing import List, Union
from .projection import AnnualGrowthPoint


class Metric(BaseModel):
    name: str
    value: str
    context: str


class ProjectionMetric(BaseModel):
    name: str
    context: str
    data: List[AnnualGrowthPoint]


MetricResponse = Union[Metric, ProjectionMetric]
