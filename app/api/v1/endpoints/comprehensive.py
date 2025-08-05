from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging

from app.models.spellcheck import Correction
from app.models.improvement import Suggestion
from app.services.integrated_service import get_integrated_service
from app.core.config import settings
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter()

class ComprehensiveRequest(BaseModel):
    text: str = Field(..., description="검사할 텍스트", max_length=1000)
    include_improvement: bool = Field(True, description="문장 개선 추천 포함 여부")
    style: str = Field("formal", description="개선 스타일 (formal, casual, academic, business)")

class ComprehensiveResponse(BaseModel):
    original_text: str
    corrected_text: str
    corrections: list[Correction]
    improvements: Optional[Dict[str, Any]] = None
    has_errors: bool
    total_corrections: int
    status: str
    message: str

@router.post(
    "/comprehensive", 
    response_model=ComprehensiveResponse,
    summary="종합 텍스트 검사",
    description="맞춤법 교정, 타이포 교정, 문장 개선을 모두 수행하는 종합 검사 서비스"
)
async def comprehensive_check(request: ComprehensiveRequest):
    """
    종합적인 텍스트 검사 및 개선
    
    - **text**: 검사할 텍스트 (최대 1000자)
    - **include_improvement**: 문장 개선 추천 포함 여부 (기본값: True)
    - **style**: 개선 스타일 (formal, casual, academic, business)
    
    맞춤법 교정과 문장 개선을 동시에 수행하여 최적의 결과를 제공합니다.
    """
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
        
        # 종합 검사 수행
        logger.info(f"Comprehensive check request: {len(request.text)} chars, improvement: {request.include_improvement}")
        
        result = get_integrated_service().comprehensive_check(
            text=request.text,
            include_improvement=request.include_improvement,
            style=request.style
        )
        
        if result["status"] == "error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "종합 검사 중 오류가 발생했습니다.")
            )
        
        # Correction 객체 변환
        corrections = []
        for correction in result["corrections"]:
            if isinstance(correction, dict):
                corrections.append(Correction(**correction))
            else:
                corrections.append(correction)
        
        # 응답 생성
        response = ComprehensiveResponse(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            corrections=corrections,
            improvements=result["improvements"],
            has_errors=len(corrections) > 0,
            total_corrections=len(corrections),
            status="success",
            message=f"종합 검사가 완료되었습니다. {len(corrections)}개의 교정사항을 발견했습니다."
        )
        
        logger.info(f"Comprehensive check completed: {len(corrections)} corrections")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in comprehensive check: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "message": "종합 검사 중 오류가 발생했습니다.",
                "detail": str(e)
            }
        )

@router.get(
    "/health",
    summary="종합 서비스 상태 확인",
    description="모든 텍스트 검사 서비스의 상태를 확인합니다."
)
async def comprehensive_health_check():
    """모든 서비스의 종합적인 상태 확인"""
    try:
        health_status = get_integrated_service().is_healthy()
        
        overall_healthy = all(health_status.values())
        
        return {
            "status": "healthy" if overall_healthy else "partial",
            "services": health_status,
            "message": "모든 서비스가 정상 동작중입니다." if overall_healthy else "일부 서비스에 문제가 있습니다.",
            "details": {
                "primary_spell_check": "theSOL1/kogrammar-base 맞춤법 교정",
                "improvement_service": "theSOL1/kogrammar-base 문장 개선", 
                "typo_corrector": "j5ng/et5-typos-corrector 보조 교정"
            }
        }
        
    except Exception as e:
        logger.error(f"Comprehensive health check failed: {e}")
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
    summary="종합 서비스 정보",
    description="모든 텍스트 검사 및 개선 서비스의 정보를 제공합니다."
)
async def comprehensive_service_info():
    """종합 서비스 정보"""
    return {
        "service": "FixMe 종합 텍스트 검사",
        "version": "1.0.0",
        "models": {
            "primary": {
                "name": settings.generative_model_name,
                "purpose": "맞춤법 교정 및 문장 개선"
            },
            "secondary": {
                "name": settings.secondary_model_name,
                "purpose": "보조 타이포 교정"
            }
        },
        "features": [
            "맞춤법 교정",
            "타이포 교정 (보조)",
            "문장 개선 추천",
            "다양한 문체 지원",
            "병렬 처리"
        ],
        "supported_styles": ["formal", "casual", "academic", "business"],
        "max_text_length": settings.max_text_length,
        "endpoints": {
            "comprehensive": "/api/v1/comprehensive/comprehensive",
            "spellcheck_only": "/api/v1/spellcheck/check", 
            "improvement_only": "/api/v1/improvement/text"
        }
    }