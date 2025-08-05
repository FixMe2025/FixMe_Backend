from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from app.models.improvement import ImprovementRequest, ImprovementResponse, Suggestion
from app.services.integrated_service import get_integrated_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/text", response_model=ImprovementResponse)
async def improve_text(request: ImprovementRequest) -> ImprovementResponse:
    """
    한글 생성형 모델을 사용하여 텍스트를 개선합니다.
    
    - **text**: 개선할 텍스트 (최대 1000자)
    - **style**: 문체 스타일 (formal, casual, academic, business)
    """
    try:
        logger.info(f"Text improvement request received: {len(request.text)} characters")
        
        # 텍스트 개선 서비스 호출 (통합 서비스 사용)
        result = get_integrated_service().quick_improvement(request.text, request.style)
        
        # 에러가 있는 경우 처리
        if "error" in result:
            raise HTTPException(status_code=500, detail=f"Text improvement failed: {result['error']}")
        
        # 응답 생성
        suggestions = [
            Suggestion(text=suggestion["text"], confidence=suggestion["confidence"])
            for suggestion in result["suggestions"]
        ]
        
        return ImprovementResponse(
            original_text=result["original_text"],
            improved_text=result["improved_text"],
            suggestions=suggestions,
            style_applied=result["style_applied"],
            message="문장 개선이 완료되었습니다."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in text improvement: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    문장 개선 서비스의 상태를 확인합니다.
    """
    try:
        health_status = get_integrated_service().is_healthy()
        is_healthy = health_status["improvement_service"]
        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "service": "text_improvement",
            "model_loaded": get_integrated_service().improvement_service.model is not None,
            "all_services": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "text_improvement",
            "error": str(e)
        }

@router.get("/info")
async def service_info() -> Dict[str, Any]:
    """
    문장 개선 서비스의 정보를 제공합니다.
    """
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        return {
            "service": "text_improvement",
            "version": "1.0.0",
            "model": settings.generative_model_name,
            "max_text_length": settings.max_text_length,
            "supported_styles": ["formal", "casual", "academic", "business"],
            "device": get_integrated_service().improvement_service.device
        }
    except Exception as e:
        logger.error(f"Failed to get service info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service information")