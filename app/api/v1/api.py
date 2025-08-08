from fastapi import APIRouter

from app.api.v1.endpoints import pipeline, comprehensive

api_router = APIRouter()
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])
api_router.include_router(comprehensive.router, prefix="/comprehensive", tags=["comprehensive"])