from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import (
    CandidateProduct,
    DecisionNarrative,
    FinalEntryCard,
    RequestSession,
    ReviewSummary,
)
from app.services import engine, tournament as tournament_service

router = APIRouter()


class SessionCreate(BaseModel):
    """PRD STEP 1~5 사용자 입력."""

    category_id: str
    budget: int = Field(gt=0, description="목표 예산 (원)")
    budget_tolerance_pct: int = Field(default=10, ge=0, le=50, description="허용 오차 (%)")
    usage_text: str = Field(min_length=1, max_length=2000, description="용도 (자연어)")
    priorities: list[str] = Field(default_factory=list, max_length=3, description="1~3순위")
    tournament_size: int = Field(default=0, description="2/4/8/16, 0=Auto")


class SessionOut(BaseModel):
    id: str
    category_id: str
    budget: int
    budget_tolerance_pct: int
    usage_text: str
    priorities: list[str]
    tournament_size: int
    engine_phase: str
    spec_sheet: dict | None = None

    model_config = {"from_attributes": True}


class ReviewOut(BaseModel):
    summary: str
    sources: list[str]
    fit_score: int
    budget_score: int
    satisfaction_score: int
    missing_required: bool
    critical_flaw: str | None

    model_config = {"from_attributes": True}


class CandidateOut(BaseModel):
    id: str
    name: str
    brand: str
    price: int
    specs: dict
    source: str
    status: str
    elimination_reason: str | None = None
    review: ReviewOut | None = None

    model_config = {"from_attributes": True}


def _attach_reviews(db: Session, candidates: list[CandidateProduct]) -> list[CandidateOut]:
    reviews = {
        r.candidate_id: r
        for r in db.query(ReviewSummary)
        .filter(ReviewSummary.candidate_id.in_([c.id for c in candidates]))
        .all()
    }
    return [
        CandidateOut.model_validate(c, from_attributes=True).model_copy(
            update={
                "review": (
                    ReviewOut.model_validate(reviews[c.id], from_attributes=True)
                    if c.id in reviews
                    else None
                )
            }
        )
        for c in candidates
    ]


@router.post("", response_model=SessionOut, status_code=201)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)) -> RequestSession:
    if payload.tournament_size not in (0, 2, 4, 8, 16):
        raise HTTPException(status_code=422, detail="tournament_size must be 2/4/8/16 or 0 (Auto)")
    session = RequestSession(**payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: str, db: Session = Depends(get_db)) -> RequestSession:
    session = db.get(RequestSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session


def _get_session_or_404(db: Session, session_id: str) -> RequestSession:
    session = db.get(RequestSession, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session


@router.post("/{session_id}/plan", response_model=SessionOut)
def run_plan(session_id: str, db: Session = Depends(get_db)) -> RequestSession:
    """Phase 1. PLAN — 최적 사양서 생성."""
    session = _get_session_or_404(db, session_id)
    engine.run_plan(db, session)
    return session


@router.post("/{session_id}/research", response_model=list[CandidateOut])
def run_research(session_id: str, db: Session = Depends(get_db)) -> list[CandidateOut]:
    """Phase 2. RESEARCH — 시장 후보군 수집."""
    session = _get_session_or_404(db, session_id)
    return _attach_reviews(db, engine.run_research(db, session))


@router.post("/{session_id}/review-scan", response_model=list[CandidateOut])
def run_review_scan(session_id: str, db: Session = Depends(get_db)) -> list[CandidateOut]:
    """Phase 3. REVIEW SCAN — 후보별 후기 요약/평가."""
    session = _get_session_or_404(db, session_id)
    engine.run_review_scan(db, session)
    return _attach_reviews(db, engine.session_candidates(db, session))


@router.post("/{session_id}/list-up", response_model=list[CandidateOut])
def run_list_up(session_id: str, db: Session = Depends(get_db)) -> list[CandidateOut]:
    """Phase 4. LIST UP — 자동 탈락 적용."""
    session = _get_session_or_404(db, session_id)
    return _attach_reviews(db, engine.run_list_up(db, session))


@router.get("/{session_id}/candidates", response_model=list[CandidateOut])
def list_candidates(session_id: str, db: Session = Depends(get_db)) -> list[CandidateOut]:
    _get_session_or_404(db, session_id)
    candidates = (
        db.query(CandidateProduct)
        .filter(CandidateProduct.session_id == session_id)
        .order_by(CandidateProduct.price)
        .all()
    )
    return _attach_reviews(db, candidates)


class NarrativeOut(BaseModel):
    narrative: str
    story: str
    digging_scores: dict
    sources: list[str]
    ai_inferred: bool

    model_config = {"from_attributes": True}


class CardOut(BaseModel):
    candidate_id: str
    name: str
    brand: str
    price: int
    headline: str
    key_specs: list[str]
    pros: list[str]
    cons: list[str]
    review_digest: str
    worldview: str
    recommended_for: list[str]
    not_recommended_for: list[str]
    narrative: NarrativeOut | None = None


def _build_cards(db: Session, session: RequestSession) -> list[CardOut]:
    candidates = engine.shortlisted_candidates(db, session)
    candidate_ids = [c.id for c in candidates]
    cards = {
        card.candidate_id: card
        for card in db.query(FinalEntryCard)
        .filter(FinalEntryCard.candidate_id.in_(candidate_ids))
        .all()
    }
    narratives = {
        n.candidate_id: n
        for n in db.query(DecisionNarrative)
        .filter(DecisionNarrative.candidate_id.in_(candidate_ids))
        .all()
    }
    result = []
    for c in candidates:
        card = cards.get(c.id)
        if card is None:
            continue
        narrative = narratives.get(c.id)
        result.append(
            CardOut(
                candidate_id=c.id,
                name=c.name,
                brand=c.brand,
                price=c.price,
                headline=card.headline,
                key_specs=card.key_specs,
                pros=card.pros,
                cons=card.cons,
                review_digest=card.review_digest,
                worldview=card.worldview,
                recommended_for=card.recommended_for,
                not_recommended_for=card.not_recommended_for,
                narrative=(
                    NarrativeOut.model_validate(narrative, from_attributes=True)
                    if narrative
                    else None
                ),
            )
        )
    return result


@router.post("/{session_id}/digging", response_model=list[CandidateOut])
def run_digging(session_id: str, db: Session = Depends(get_db)) -> list[CandidateOut]:
    """Phase 5. DIGGING — 세계관 조사 / Decision Narrative."""
    session = _get_session_or_404(db, session_id)
    engine.run_digging(db, session)
    return _attach_reviews(db, engine.session_candidates(db, session))


@router.post("/{session_id}/final-entry", response_model=list[CardOut])
def run_final_entry(session_id: str, db: Session = Depends(get_db)) -> list[CardOut]:
    """Phase 6. FINAL ENTRY — 최종 카드 생성."""
    session = _get_session_or_404(db, session_id)
    engine.run_final_entry(db, session)
    return _build_cards(db, session)


@router.get("/{session_id}/cards", response_model=list[CardOut])
def list_cards(session_id: str, db: Session = Depends(get_db)) -> list[CardOut]:
    session = _get_session_or_404(db, session_id)
    return _build_cards(db, session)


class MatchOut(BaseModel):
    id: str
    round_no: int
    match_no: int
    candidate_a_id: str
    candidate_b_id: str
    winner_candidate_id: str | None
    choice_reason: str | None

    model_config = {"from_attributes": True}


class TournamentOut(BaseModel):
    id: str
    size: int
    status: str
    winner_candidate_id: str | None
    matches: list[MatchOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class ChoicePayload(BaseModel):
    winner_candidate_id: str
    reason: str | None = Field(default=None, max_length=1000, description="선택 이유")


def _tournament_out(db: Session, t) -> TournamentOut:
    return TournamentOut.model_validate(t, from_attributes=True).model_copy(
        update={
            "matches": [
                MatchOut.model_validate(m, from_attributes=True)
                for m in tournament_service.matches(db, t)
            ]
        }
    )


@router.post("/{session_id}/tournament", response_model=TournamentOut, status_code=201)
def create_tournament(session_id: str, db: Session = Depends(get_db)) -> TournamentOut:
    """Phase 7. CHOICE — 토너먼트 생성."""
    session = _get_session_or_404(db, session_id)
    t = tournament_service.create_tournament(db, session)
    return _tournament_out(db, t)


@router.get("/{session_id}/tournament", response_model=TournamentOut)
def get_tournament(session_id: str, db: Session = Depends(get_db)) -> TournamentOut:
    session = _get_session_or_404(db, session_id)
    t = tournament_service.get_tournament(db, session)
    return _tournament_out(db, t)


@router.post(
    "/{session_id}/tournament/matches/{match_id}/choose",
    response_model=TournamentOut,
)
def choose_winner(
    session_id: str,
    match_id: str,
    payload: ChoicePayload,
    db: Session = Depends(get_db),
) -> TournamentOut:
    """A vs B에서 사용자의 선택을 기록한다."""
    session = _get_session_or_404(db, session_id)
    t = tournament_service.get_tournament(db, session)
    t = tournament_service.choose_winner(
        db, t, match_id, payload.winner_candidate_id, payload.reason
    )
    return _tournament_out(db, t)
