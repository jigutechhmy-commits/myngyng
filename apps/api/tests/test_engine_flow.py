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


def test_full_engine_flow(session_id: str):
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

    # Phase 3. REVIEW SCAN
    res = client.post(f"/api/sessions/{session_id}/review-scan")
    assert res.status_code == 200
    reviewed = res.json()
    assert all(c["review"] is not None for c in reviewed)
    assert all(1 <= c["review"]["satisfaction_score"] <= 5 for c in reviewed)
    assert all(c["review"]["sources"] for c in reviewed)

    # Phase 4. LIST UP — 자동 탈락 검증
    res = client.post(f"/api/sessions/{session_id}/list-up")
    assert res.status_code == 200
    final = {c["name"]: c for c in res.json()}

    # 예산 2,500,000 ±10% → 상한 2,750,000원
    assert final["MacBook Pro 14 (M4 Pro)"]["elimination_reason"] == "budget_exceeded"
    # ARM/필수 기능 미달
    assert final["Surface Pro 11"]["elimination_reason"] == "missing_required"
    assert final["Surface Laptop 7"]["elimination_reason"] == "missing_required"
    # 낮은 만족도 (<=2)
    assert final["Swift Go 14 AI"]["elimination_reason"] == "low_satisfaction"
    # 통과 후보
    assert final["ThinkPad X1 Carbon Gen 13"]["status"] == "shortlisted"
    assert final["ROG Zephyrus G14"]["status"] == "shortlisted"

    shortlisted = [c for c in final.values() if c["status"] == "shortlisted"]
    assert len(shortlisted) >= 4

    # Phase 5. DIGGING — Decision Narrative
    res = client.post(f"/api/sessions/{session_id}/digging")
    assert res.status_code == 200

    # Phase 6. FINAL ENTRY — 최종 카드
    res = client.post(f"/api/sessions/{session_id}/final-entry")
    assert res.status_code == 200
    cards = res.json()
    assert len(cards) == len(shortlisted)
    for card in cards:
        assert card["headline"]
        assert card["pros"] and card["cons"]
        assert card["recommended_for"]
        assert card["narrative"]["narrative"]
        scores = card["narrative"]["digging_scores"]
        assert set(scores) == {
            "philosophy", "history", "fandom", "originality", "community", "story"
        }
        assert all(0 <= v <= 10 for v in scores.values())
        assert card["narrative"]["ai_inferred"] is True  # Fact Shield 표기

    # 카드 조회
    assert len(client.get(f"/api/sessions/{session_id}/cards").json()) == len(cards)
    assert client.get(f"/api/sessions/{session_id}").json()["engine_phase"] == "final_entry"

    # Phase 7. CHOICE — 토너먼트 (8강 요청, 통과 6명 → 4강 브래킷)
    res = client.post(f"/api/sessions/{session_id}/tournament")
    assert res.status_code == 201
    t = res.json()
    assert t["size"] == 4
    assert t["status"] == "active"
    assert len(t["matches"]) == 2

    # 중복 생성 거부
    assert client.post(f"/api/sessions/{session_id}/tournament").status_code == 409

    # 결승까지 항상 A를 선택
    while t["status"] == "active":
        match = next(m for m in t["matches"] if m["winner_candidate_id"] is None)
        res = client.post(
            f"/api/sessions/{session_id}/tournament/matches/{match['id']}/choose",
            json={"winner_candidate_id": match["candidate_a_id"], "reason": "테스트 선택"},
        )
        assert res.status_code == 200
        t = res.json()

    assert t["winner_candidate_id"] is not None
    assert len(t["matches"]) == 3  # 4강 2매치 + 결승 1매치
    assert all(m["winner_candidate_id"] for m in t["matches"])

    # 종료 후 추가 선택 거부
    last = t["matches"][-1]
    res = client.post(
        f"/api/sessions/{session_id}/tournament/matches/{last['id']}/choose",
        json={"winner_candidate_id": last["candidate_a_id"]},
    )
    assert res.status_code == 409

    # 세션 phase 확인
    assert client.get(f"/api/sessions/{session_id}").json()["engine_phase"] == "choice"

    # Decision Journal — 선택 기록 + Choice Confidence
    res = client.post(f"/api/sessions/{session_id}/journal")
    assert res.status_code == 201
    journal = res.json()
    assert journal["winner_candidate_id"] == t["winner_candidate_id"]
    assert len(journal["choice_log"]) == 3
    assert journal["choice_log"][0]["reason"] == "테스트 선택"
    conf = journal["confidence"]
    assert conf["long_term"] is None  # 재조사 전
    assert conf["fit"] and conf["budget"] and conf["review"]
    assert conf["overall"] == round((conf["fit"] + conf["budget"] + conf["review"]) / 3)
    assert journal["followup_due_at"]

    # 중복 생성 거부, phase=done
    assert client.post(f"/api/sessions/{session_id}/journal").status_code == 409
    assert client.get(f"/api/sessions/{session_id}").json()["engine_phase"] == "done"

    # 6개월 후 만족도 재조사
    res = client.post(
        f"/api/sessions/{session_id}/journal/followup", json={"satisfaction": 4}
    )
    assert res.status_code == 200
    journal = res.json()
    assert journal["followup_satisfaction"] == 4
    assert journal["confidence"]["long_term"] == 80
    assert journal["followup_answered_at"]

    # 재조사 중복 응답 거부
    res = client.post(
        f"/api/sessions/{session_id}/journal/followup", json={"satisfaction": 5}
    )
    assert res.status_code == 409


def test_research_requires_plan(session_id: str):
    res = client.post(f"/api/sessions/{session_id}/research")
    assert res.status_code == 409
