from pydantic import BaseModel
from typing import List, Optional, Dict


class CorrectionRequest(BaseModel):
    text: str


class Correction(BaseModel):
    original: str
    corrected: str
    type: str


class Suggestion(BaseModel):
    type: str
    original: str
    suggestion: str
    reason: str


class CorrectionResponse(BaseModel):
    original_text: str
    corrected_text: str
    corrections: List[Correction]
    suggestions: Optional[List[Suggestion]] = []
    stage_texts: Optional[dict] = None


class HealthResponse(BaseModel):
    status: str
    is_model_loaded: bool
    device: str


# 종합 교정 관련 모델들
class ComprehensiveRequest(BaseModel):
    text: str
    target_style: Optional[str] = None  # 특정 문체 지정 (선택사항)


class StyleImprovement(BaseModel):
    original: str
    improved: str
    type: str
    position: Optional[int] = None


class StyleOption(BaseModel):
    name: str
    description: str
    example_transforms: List[Dict[str, str]]


class ComprehensiveResponse(BaseModel):
    original_text: str
    corrected_text: str
    styled_text: Optional[str] = None
    target_style: Optional[str] = None
    spellcheck_corrections: List[Correction]
    style_suggestions: Optional[Dict[str, str]] = None
    available_styles: Optional[List[str]] = None
    style_applied: bool = False
    improvements_made: Optional[List[StyleImprovement]] = None
    error: Optional[str] = None