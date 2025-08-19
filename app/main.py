from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.langgraph_pipeline import get_langgraph_pipeline

# 애플리케이션의 엔트리 포인트
# 로깅 설정
setup_logging()

app = FastAPI(
    title="FixMe - 맞춤법 교정 API",
    description="한글 맞춤법 교정을 위한 FastAPI 서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 모델을 미리 로딩"""
    logger.info("Starting model pre-loading...")
    try:
        # 모델 사전 로딩
        pipeline = get_langgraph_pipeline()
        logger.info("✅ Models pre-loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to pre-load models: {e}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FixMe 건강함!"}

@app.get("/")
async def root():
    return {"message": "FixMe - 한글 맞춤법 교정 API", "docs": "/docs"}
