"""Good Choice Engine — Phase 실행 오케스트레이션."""

import json
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai import prompts
from app.ai.provider import get_provider
from app.models import CandidateProduct, RequestSession

SHARED_CATEGORIES_DIR = Path(__file__).resolve().parents[4] / "packages" / "shared" / "categories"


def _category_detail(category_id: str) -> dict:
    path = SHARED_CATEGORIES_DIR / f"{category_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="category not found")
    return json.loads(path.read_text(encoding="utf-8"))


def _require_phase(session: RequestSession, expected: str) -> None:
    if session.engine_phase != expected:
        raise HTTPException(
            status_code=409,
            detail=f"engine_phase must be '{expected}' (current: '{session.engine_phase}')",
        )


def run_plan(db: Session, session: RequestSession) -> dict:
    """Phase 1. PLAN — 최적 사양서 생성."""
    _require_phase(session, "created")
    category = _category_detail(session.category_id)

    spec_sheet = get_provider().complete_json(
        system=prompts.PLAN_SYSTEM,
        user=prompts.plan_user_prompt(
            category_name=category["name_ko"],
            spec_fields=category["spec_schema"]["fields"],
            budget=session.budget,
            tolerance_pct=session.budget_tolerance_pct,
            usage_text=session.usage_text,
            priorities=session.priorities,
        ),
        schema=prompts.PLAN_SCHEMA,
    )

    session.spec_sheet = spec_sheet
    session.engine_phase = "plan"
    db.commit()
    db.refresh(session)
    return spec_sheet


def run_research(db: Session, session: RequestSession) -> list[CandidateProduct]:
    """Phase 2. RESEARCH — 시장 후보군 수집."""
    _require_phase(session, "plan")
    category = _category_detail(session.category_id)

    result = get_provider().complete_json(
        system=prompts.RESEARCH_SYSTEM,
        user=prompts.research_user_prompt(
            category_name=category["name_ko"],
            spec_sheet=session.spec_sheet or {},
            budget=session.budget,
            tolerance_pct=session.budget_tolerance_pct,
        ),
        schema=prompts.RESEARCH_SCHEMA,
    )

    candidates = [
        CandidateProduct(
            session_id=session.id,
            name=item["name"],
            brand=item["brand"],
            price=item["price"],
            specs=item.get("specs", {}),
            source="ai",
        )
        for item in result["candidates"]
    ]
    db.add_all(candidates)
    session.engine_phase = "research"
    db.commit()
    for candidate in candidates:
        db.refresh(candidate)
    return candidates
