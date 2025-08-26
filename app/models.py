from pydantic import BaseModel
from typing import List, Optional


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