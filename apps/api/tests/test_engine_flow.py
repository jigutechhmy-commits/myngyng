"""세션 생성 → PLAN → RESEARCH 엔드투엔드 플로우 (MockProvider 사용)."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

SESSION_PAYLOAD = {
    "category_id": "laptop",
    "budget": 2500000,
    "budget_tolerance_pct": 10,
    "usage_text": "Fusion360 설계, 소규모 바이브코딩, 휴대성",
    "priorities": ["performance", "portability", "battery"],
    "tournament_size": 8,
}


@pytest.fixture()
def session_id() -> str:
    res = client.post("/api/sessions", json=SESSION_PAYLOAD)
    assert res.status_code == 201
    return res.json()["id"]


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_categories():
    categories = client.get("/api/categories").json()["categories"]
    assert any(c["id"] == "laptop" and c["enabled"] for c in categories)
    detail = client.get("/api/categories/laptop").json()
    assert detail["spec_schema"]["fields"]


def test_plan_then_research(session_id: str):
    # Phase 1. PLAN
    res = client.post(f"/api/sessions/{session_id}/plan")
    assert res.status_code == 200
    body = res.json()
    assert body["engine_phase"] == "plan"
    assert body["spec_sheet"]["fields"]

    # PLAN 재실행은 거부 (phase 가드)
    assert client.post(f"/api/sessions/{session_id}/plan").status_code == 409

    # Phase 2. RESEARCH
    res = client.post(f"/api/sessions/{session_id}/research")
    assert res.status_code == 200
    candidates = res.json()
    assert len(candidates) >= 8
    assert all(c["source"] == "ai" for c in candidates)

    # 후보 조회
    res = client.get(f"/api/sessions/{session_id}/candidates")
    assert res.status_code == 200
    assert len(res.json()) == len(candidates)

    # 세션 phase 갱신 확인
    assert client.get(f"/api/sessions/{session_id}").json()["engine_phase"] == "research"


def test_research_requires_plan(session_id: str):
    res = client.post(f"/api/sessions/{session_id}/research")
    assert res.status_code == 409
