from fastapi import APIRouter

from app.api.v1.endpoints import spellcheck, improvement, comprehensive

api_router = APIRouter()
api_router.include_router(spellcheck.router, prefix="/spellcheck", tags=["spellcheck"])
api_router.include_router(improvement.router, prefix="/improve", tags=["improvement"])
api_router.include_router(comprehensive.router, prefix="/comprehensive", tags=["comprehensive"])