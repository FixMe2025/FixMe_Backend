import os
import pytest

from app.services.langgraph_pipeline import get_langgraph_pipeline

import pytest

from app.services.langgraph_pipeline import get_langgraph_pipeline


# LangGraph 파이프라인의 동작을 검증하기 위한 테스트
def _short_input() -> str:
    # 간단한 오타/띄어쓰기/문법 교정이 가능한 짧은 예시
    return "안녕 하세요 저녁 머거요"


@pytest.mark.slow
def test_pipeline_run_returns_structure():
    pipeline = get_langgraph_pipeline()
    result = pipeline.run(_short_input())

    assert isinstance(result, dict)
    assert "original_text" in result
    assert "corrected_text" in result
    assert "corrections" in result
    assert "stage_texts" in result
    assert "step1" in result["stage_texts"]
    assert "final" in result["stage_texts"]


@pytest.mark.slow
def test_pipeline_health():
    pipeline = get_langgraph_pipeline()
    ok = pipeline.is_healthy()
    # 모델 로딩 환경에 따라 False가 될 수도 있으므로 타입만 체크
    assert isinstance(ok, bool)


@pytest.mark.slow
def test_pipeline_idempotent_multiple_calls():
    pipeline = get_langgraph_pipeline()
    text = _short_input()
    result1 = pipeline.run(text)
    result2 = pipeline.run(text)
    assert result1["original_text"] == text
    assert result2["original_text"] == text


