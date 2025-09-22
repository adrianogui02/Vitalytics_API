from pydantic import BaseModel
from typing import Optional


class AnnualGrowthPoint(BaseModel):
    year: int
    case_count: int
    percentage_change: Optional[float] = None

    class Config:
        from_attributes = True
