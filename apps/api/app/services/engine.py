"""Good Choice Engine — Phase 실행 오케스트레이션."""

import json
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai import prompts
from app.ai.provider import get_provider
from app.models import (
    CandidateProduct,
    DecisionNarrative,
    FinalEntryCard,
    RequestSession,
    ReviewSummary,
)

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


def session_candidates(db: Session, session: RequestSession) -> list[CandidateProduct]:
    return (
        db.query(CandidateProduct)
        .filter(CandidateProduct.session_id == session.id)
        .all()
    )


def run_review_scan(db: Session, session: RequestSession) -> list[ReviewSummary]:
    """Phase 3. REVIEW SCAN — 후보별 후기 요약/평가."""
    _require_phase(session, "research")
    category = _category_detail(session.category_id)
    candidates = session_candidates(db, session)
    if not candidates:
        raise HTTPException(status_code=409, detail="no candidates to review")

    result = get_provider().complete_json(
        system=prompts.REVIEW_SCAN_SYSTEM,
        user=prompts.review_scan_user_prompt(
            category_name=category["name_ko"],
            spec_sheet=session.spec_sheet or {},
            budget=session.budget,
            tolerance_pct=session.budget_tolerance_pct,
            usage_text=session.usage_text,
            candidates=[
                {"name": c.name, "brand": c.brand, "price": c.price, "specs": c.specs}
                for c in candidates
            ],
        ),
        schema=prompts.REVIEW_SCAN_SCHEMA,
    )

    by_name = {c.name: c for c in candidates}
    reviews: list[ReviewSummary] = []
    for item in result["reviews"]:
        candidate = by_name.get(item["name"])
        if candidate is None:
            continue  # AI가 입력에 없는 이름을 반환한 경우는 버린다
        reviews.append(
            ReviewSummary(
                candidate_id=candidate.id,
                summary=item["summary"],
                sources=item.get("sources", []),
                fit_score=item["fit_score"],
                budget_score=item["budget_score"],
                satisfaction_score=item["satisfaction_score"],
                missing_required=item.get("missing_required", False),
                critical_flaw=item.get("critical_flaw"),
            )
        )
    db.add_all(reviews)
    session.engine_phase = "review_scan"
    db.commit()
    for review in reviews:
        db.refresh(review)
    return reviews


# LIST UP 자동 탈락 기준 (PRD Phase 4)
LOW_SATISFACTION_THRESHOLD = 2


def run_list_up(db: Session, session: RequestSession) -> list[CandidateProduct]:
    """Phase 4. LIST UP — 자동 탈락 적용해 1차 후보 압축."""
    _require_phase(session, "review_scan")
    candidates = session_candidates(db, session)
    reviews = {
        r.candidate_id: r
        for r in db.query(ReviewSummary)
        .filter(ReviewSummary.candidate_id.in_([c.id for c in candidates]))
        .all()
    }
    budget_cap = session.budget * (100 + session.budget_tolerance_pct) // 100

    for candidate in candidates:
        review = reviews.get(candidate.id)
        reason = None
        if candidate.price > budget_cap:
            reason = "budget_exceeded"
        elif review is None:
            reason = "no_review"
        elif review.missing_required:
            reason = "missing_required"
        elif review.critical_flaw:
            reason = "critical_flaw"
        elif review.satisfaction_score <= LOW_SATISFACTION_THRESHOLD:
            reason = "low_satisfaction"

        if reason:
            candidate.status = "eliminated"
            candidate.elimination_reason = reason
        else:
            candidate.status = "shortlisted"

    session.engine_phase = "list_up"
    db.commit()
    for candidate in candidates:
        db.refresh(candidate)
    return candidates


def shortlisted_candidates(db: Session, session: RequestSession) -> list[CandidateProduct]:
    return (
        db.query(CandidateProduct)
        .filter(
            CandidateProduct.session_id == session.id,
            CandidateProduct.status == "shortlisted",
        )
        .all()
    )


def run_digging(db: Session, session: RequestSession) -> list[DecisionNarrative]:
    """Phase 5. DIGGING — 제품 세계관 조사, Decision Narrative 생성."""
    _require_phase(session, "list_up")
    category = _category_detail(session.category_id)
    candidates = shortlisted_candidates(db, session)
    if not candidates:
        raise HTTPException(status_code=409, detail="no shortlisted candidates")

    result = get_provider().complete_json(
        system=prompts.DIGGING_SYSTEM,
        user=prompts.digging_user_prompt(
            category_name=category["name_ko"],
            candidates=[{"name": c.name, "brand": c.brand} for c in candidates],
        ),
        schema=prompts.DIGGING_SCHEMA,
    )

    by_name = {c.name: c for c in candidates}
    narratives: list[DecisionNarrative] = []
    for item in result["narratives"]:
        candidate = by_name.get(item["name"])
        if candidate is None:
            continue
        narratives.append(
            DecisionNarrative(
                candidate_id=candidate.id,
                narrative=item["narrative"],
                story=item["story"],
                digging_scores=item["digging_scores"],
                sources=item.get("sources", []),
                ai_inferred=True,  # Fact Shield: MVP는 AI 생성 콘텐츠임을 표기
            )
        )
    db.add_all(narratives)
    session.engine_phase = "digging"
    db.commit()
    for narrative in narratives:
        db.refresh(narrative)
    return narratives


def run_final_entry(db: Session, session: RequestSession) -> list[FinalEntryCard]:
    """Phase 6. FINAL ENTRY — 최종 카드 생성."""
    _require_phase(session, "digging")
    candidates = shortlisted_candidates(db, session)
    candidate_ids = [c.id for c in candidates]
    reviews = {
        r.candidate_id: r
        for r in db.query(ReviewSummary)
        .filter(ReviewSummary.candidate_id.in_(candidate_ids))
        .all()
    }
    narratives = {
        n.candidate_id: n
        for n in db.query(DecisionNarrative)
        .filter(DecisionNarrative.candidate_id.in_(candidate_ids))
        .all()
    }

    result = get_provider().complete_json(
        system=prompts.FINAL_ENTRY_SYSTEM,
        user=prompts.final_entry_user_prompt(
            usage_text=session.usage_text,
            priorities=session.priorities,
            candidates=[
                {
                    "name": c.name,
                    "brand": c.brand,
                    "price": c.price,
                    "specs": c.specs,
                    "review": reviews[c.id].summary if c.id in reviews else None,
                    "narrative": narratives[c.id].narrative if c.id in narratives else None,
                    "story": narratives[c.id].story if c.id in narratives else None,
                }
                for c in candidates
            ],
        ),
        schema=prompts.FINAL_ENTRY_SCHEMA,
    )

    by_name = {c.name: c for c in candidates}
    cards: list[FinalEntryCard] = []
    for item in result["cards"]:
        candidate = by_name.get(item["name"])
        if candidate is None:
            continue
        cards.append(
            FinalEntryCard(
                candidate_id=candidate.id,
                headline=item["headline"],
                key_specs=item.get("key_specs", []),
                pros=item.get("pros", []),
                cons=item.get("cons", []),
                review_digest=item["review_digest"],
                worldview=item["worldview"],
                recommended_for=item.get("recommended_for", []),
                not_recommended_for=item.get("not_recommended_for", []),
            )
        )
    db.add_all(cards)
    session.engine_phase = "final_entry"
    db.commit()
    for card in cards:
        db.refresh(card)
    return cards
