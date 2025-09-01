from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import (
    CorrectionRequest, CorrectionResponse, HealthResponse, Correction, Suggestion,
    ComprehensiveRequest, ComprehensiveResponse, StyleImprovement, StyleOption
)
from .advanced_spellcheck_service import (
    advanced_spellcheck_service as spellcheck_service,
)
from .comprehensive_style_service import comprehensive_style_service
from .config import settings

app = FastAPI(
    title="FixMe 맞춤법 교정 API",
    description="theSOL1/kogrammar-base 모델을 사용한 한국어 맞춤법 교정 서비스",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """서버 상태 확인"""
    return HealthResponse(
        status="healthy" if spellcheck_service.is_model_loaded() else "unhealthy",
        is_model_loaded=spellcheck_service.is_model_loaded(),
        device=spellcheck_service.get_device_info(),
    )


@app.post("/api/v1/pipeline/run", response_model=CorrectionResponse)
async def pipeline_run(request: CorrectionRequest):
    """기본 맞춤법 교정 API - 프론트엔드 호환"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

        result = spellcheck_service.correct_text(request.text)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        corrections = [
            Correction(
                original=correction["original"],
                corrected=correction["corrected"],
                type=correction["type"],
            )
            for correction in result["corrections"]
        ]

        suggestions = [
            Suggestion(
                type=suggestion["type"],
                original=suggestion["original"],
                suggestion=suggestion["suggestion"],
                reason=suggestion["reason"],
            )
            for suggestion in result.get("suggestions", [])
        ]

        return CorrectionResponse(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            corrections=corrections,
            suggestions=suggestions,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"서버 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/v1/comprehensive/comprehensive", response_model=ComprehensiveResponse)
async def comprehensive_correction(request: ComprehensiveRequest):
    """종합 교정 API - 맞춤법 교정 + 문체 변환"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

        result = comprehensive_style_service.comprehensive_correction(
            request.text, 
            request.target_style
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # 맞춤법 교정 결과 변환
        corrections = [
            Correction(
                original=correction["original"],
                corrected=correction["corrected"],
                type=correction["type"],
            )
            for correction in result.get("spellcheck_corrections", [])
        ]

        # 문체 개선 사항 변환
        improvements = []
        if "improvements_made" in result:
            improvements = [
                StyleImprovement(
                    original=imp["original"],
                    improved=imp["improved"],
                    type=imp["type"],
                    position=imp.get("position")
                )
                for imp in result["improvements_made"]
            ]

        return ComprehensiveResponse(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            styled_text=result.get("styled_text"),
            target_style=result.get("target_style"),
            spellcheck_corrections=corrections,
            style_suggestions=result.get("style_suggestions"),
            available_styles=result.get("available_styles"),
            style_applied=result.get("style_applied", False),
            improvements_made=improvements
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"서버 오류가 발생했습니다: {str(e)}"
        )


@app.post("/api/v1/spellcheck", response_model=CorrectionResponse)
async def spellcheck(request: CorrectionRequest):
    """맞춤법 교정 API"""
    try:
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="텍스트가 비어있습니다.")

        result = spellcheck_service.correct_text(request.text)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        corrections = [
            Correction(
                original=correction["original"],
                corrected=correction["corrected"],
                type=correction["type"],
            )
            for correction in result["corrections"]
        ]

        suggestions = [
            Suggestion(
                type=suggestion["type"],
                original=suggestion["original"],
                suggestion=suggestion["suggestion"],
                reason=suggestion["reason"],
            )
            for suggestion in result.get("suggestions", [])
        ]

        return CorrectionResponse(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            corrections=corrections,
            suggestions=suggestions,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"서버 오류가 발생했습니다: {str(e)}"
        )


@app.get("/api/v1/comprehensive/styles", response_model=List[StyleOption])
async def get_available_styles():
    """사용 가능한 문체 스타일 목록 조회"""
    try:
        styles = comprehensive_style_service.get_available_styles()
        
        return [
            StyleOption(
                name=style["name"],
                description=style["description"],
                example_transforms=style["example_transforms"]
            )
            for style in styles
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"스타일 조회 중 오류가 발생했습니다: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
