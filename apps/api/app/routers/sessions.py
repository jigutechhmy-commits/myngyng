from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.models import CandidateProduct, RequestSession
from app.services import engine

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


class CandidateOut(BaseModel):
    id: str
    name: str
    brand: str
    price: int
    specs: dict
    source: str
    status: str

    model_config = {"from_attributes": True}


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
def run_research(session_id: str, db: Session = Depends(get_db)) -> list[CandidateProduct]:
    """Phase 2. RESEARCH — 시장 후보군 수집."""
    session = _get_session_or_404(db, session_id)
    return engine.run_research(db, session)


@router.get("/{session_id}/candidates", response_model=list[CandidateOut])
def list_candidates(session_id: str, db: Session = Depends(get_db)) -> list[CandidateProduct]:
    _get_session_or_404(db, session_id)
    return (
        db.query(CandidateProduct)
        .filter(CandidateProduct.session_id == session_id)
        .order_by(CandidateProduct.price)
        .all()
    )
