# app/schemas/chart.py
from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class ChartDataPoint(BaseModel):
    group: str
    count: int

    class Config:
        from_attributes = True


class ChartResponse(BaseModel):

    filter_options: dict
    data: List[ChartDataPoint]

    class Config:
        from_attributes = True
