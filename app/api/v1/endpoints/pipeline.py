from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import logging

from app.services.langgraph_pipeline import get_langgraph_pipeline
from app.models.spellcheck import Correction


router = APIRouter()
logger = logging.getLogger(__name__)


class PipelineRequest(BaseModel):
    text: str = Field(..., description="검사할 텍스트", max_length=2000)


class PipelineResponse(BaseModel):
    original_text: str
    corrected_text: str
    corrections: list[Correction]
    stage_texts: Dict[str, str]


@router.post("/run", response_model=PipelineResponse, summary="LangGraph 파이프라인 실행")
async def run_pipeline(req: PipelineRequest):
    try:
        result = get_langgraph_pipeline().run(req.text)
        corrections = [Correction(**c) if isinstance(c, dict) else c for c in result["corrections"]]
        return PipelineResponse(
            original_text=result["original_text"],
            corrected_text=result["corrected_text"],
            corrections=corrections,
            stage_texts=result["stage_texts"],
        )
    except Exception as e:
        logger.error(f"Pipeline run failed: {e}")
        raise HTTPException(status_code=500, detail="파이프라인 실행 중 오류가 발생했습니다.")


@router.get("/health", summary="LangGraph 파이프라인 상태")
async def pipeline_health():
    try:
        healthy = get_langgraph_pipeline().is_healthy()
        return {"status": "healthy" if healthy else "unhealthy"}
    except Exception as e:
        logger.error(f"Pipeline health check error: {e}")
        return {"status": "unhealthy", "error": str(e)}


