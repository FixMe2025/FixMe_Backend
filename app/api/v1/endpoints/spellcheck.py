from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
import logging

from app.models.spellcheck import (
    SpellCheckRequest,
    SpellCheckResponse,
    ErrorResponse,
    Correction
)
from app.services.integrated_service import get_integrated_service
from app.core.config import settings

# 맞춤법 검사 기능을 제공하는 엔드포인트 모듈
logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/check",
    response_model=SpellCheckResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="맞춤법 검사",
    description="입력된 한글 텍스트의 맞춤법을 검사하고 교정 제안을 제공합니다."
)
async def check_spelling(request: SpellCheckRequest):
    try:
        # 텍스트 길이 검증
        if len(request.text) > settings.max_text_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"텍스트 길이가 최대 허용 길이({settings.max_text_length}자)를 초과했습니다."
            )
        
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="빈 텍스트는 검사할 수 없습니다."
            )
        
        # 맞춤법 검사 수행 (통합 서비스 사용)
        logger.info("Received a spell check request.")
        result = get_integrated_service().quick_spell_check(request.text)
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "맞춤법 검사 중 오류가 발생했습니다.")
            )
        
        # 응답 생성
        corrections = [Correction(**c) if isinstance(c, dict) else c for c in result["corrections"]]
        response = SpellCheckResponse(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            corrections=corrections,
            has_errors=len(corrections) > 0,
            total_corrections=len(corrections),
            message="맞춤법 검사가 완료되었습니다." if corrections else "오류가 발견되지 않았습니다."
        )
        
        logger.info(f"Found {len(corrections)} corrections")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in spell check: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "맞춤법 검사 중 오류가 발생했습니다.",
                "detail": str(e)
            }
        )


@router.get(
    "/health",
    summary="서비스 상태 확인",
    description="맞춤법 검사 서비스의 상태를 확인합니다."
)
async def health_check():
    try:
        health_status = get_integrated_service().is_healthy()
        is_healthy = health_status["primary_spell_check"]
        
        if is_healthy:
            return {
                "status": "healthy",
                "message": "맞춤법 검사 서비스가 정상 동작중입니다."
            }
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "message": "맞춤법 검사 서비스에 문제가 있습니다.",
                    "primary_model": settings.generative_model_name,
                    "secondary_model": settings.secondary_model_name
                }
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": "상태 확인 중 오류가 발생했습니다.",
                "detail": str(e)
            }
        )


@router.get(
    "/info",
    summary="서비스 정보",
    description="맞춤법 검사 서비스의 정보를 제공합니다."
)
async def service_info():
    return {
        "service": "FixMe 맞춤법 검사",
        "primary_model": settings.generative_model_name,
        "secondary_model": settings.secondary_model_name,
        "max_text_length": settings.max_text_length,
        "version": "1.0.0"
    }