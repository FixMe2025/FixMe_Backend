from typing import List, Dict, TypedDict


class GraphState(TypedDict):
    """LangGraph 워크플로우에서 사용할 상태 모델"""
    original_text: str
    corrected_text: str
    corrections: List[Dict[str, str]]
    error: str
    text_chunks: List[str]
    processed_chunks: List[str]
    suggestions: List[Dict[str, str]]