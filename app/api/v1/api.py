from fastapi import APIRouter
from app.api.v1.endpoints import metrics, charts

api_router = APIRouter()
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
api_router.include_router(charts.router, prefix="/charts", tags=["Charts"])
