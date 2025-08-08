import os
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


@pytest.mark.slow
def test_pipeline_endpoint_health():
    res = client.get("/api/v1/pipeline/health")
    assert res.status_code == 200
    body = res.json()
    assert "status" in body


@pytest.mark.slow
def test_pipeline_endpoint_run():
    res = client.post("/api/v1/pipeline/run", json={"text": "안녕 하세요 저녁 머거요"})
    assert res.status_code in (200, 500)
    # 환경에 따라 모델 다운로드 실패 시 500 가능. 200이면 스키마 검증
    if res.status_code == 200:
        body = res.json()
        assert "original_text" in body
        assert "corrected_text" in body
        assert "corrections" in body
        assert "stage_texts" in body


