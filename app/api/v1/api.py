from fastapi import APIRouter

from app.api.v1.endpoints import pipeline, comprehensive

# API 버전 1의 라우터를 생성하고 엔드포인트를 등록하는 파일
api_router = APIRouter()

# 파이프라인 실행 관련 엔드포인트 등록
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])

# 종합 교정 기능 엔드포인트 등록
api_router.include_router(comprehensive.router, prefix="/comprehensive", tags=["comprehensive"])