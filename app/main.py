from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging

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


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "FixMe 건강함!"}

@app.get("/")
async def root():
    return {"message": "FixMe - 한글 맞춤법 교정 API", "docs": "/docs"}
