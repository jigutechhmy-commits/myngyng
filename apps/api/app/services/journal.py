"""Decision Journal & Choice Confidence (PRD 5~6장)."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    CandidateProduct,
    DecisionJournalEntry,
    RequestSession,
    ReviewSummary,
    Tournament,
    TournamentMatch,
)
from app.services.tournament import get_tournament, matches

FOLLOWUP_AFTER = timedelta(days=180)  # 6개월 후 만족도 재조사


def _round_label(round_no: int, size: int) -> str:
    remaining = size >> (round_no - 1)
    return "결승" if remaining == 2 else f"{remaining}강"


def _compute_confidence(review: ReviewSummary | None) -> dict:
    """Choice Confidence (0~100).

    요구사항 적합도/예산 적합도/후기 만족도는 REVIEW SCAN 점수(1~5)를 환산한다.
    장기 만족도는 6개월 재조사 전까지 null이며, overall은 가용 항목 평균이다.
    """
    if review is None:
        return {"fit": None, "budget": None, "review": None, "long_term": None, "overall": None}

    def pct(score: int) -> int:
        return score * 20

    components = {
        "fit": pct(review.fit_score),
        "budget": pct(review.budget_score),
        "review": pct(review.satisfaction_score),
        "long_term": None,
    }
    available = [v for v in components.values() if v is not None]
    components["overall"] = round(sum(available) / len(available)) if available else None
    return components


def create_journal_entry(db: Session, session: RequestSession) -> DecisionJournalEntry:
    if session.engine_phase != "choice":
        raise HTTPException(
            status_code=409,
            detail=f"engine_phase must be 'choice' (current: '{session.engine_phase}')",
        )
    tournament = get_tournament(db, session)
    if tournament.status != "done" or tournament.winner_candidate_id is None:
        raise HTTPException(status_code=409, detail="tournament not finished")
    if (
        db.query(DecisionJournalEntry)
        .filter(DecisionJournalEntry.session_id == session.id)
        .first()
    ):
        raise HTTPException(status_code=409, detail="journal entry already exists")

    names = {
        c.id: c.name
        for c in db.query(CandidateProduct)
        .filter(CandidateProduct.session_id == session.id)
        .all()
    }
    choice_log = []
    for m in matches(db, tournament):
        loser_id = (
            m.candidate_b_id
            if m.winner_candidate_id == m.candidate_a_id
            else m.candidate_a_id
        )
        choice_log.append(
            {
                "round_label": _round_label(m.round_no, tournament.size),
                "picked": names.get(m.winner_candidate_id, ""),
                "over": names.get(loser_id, ""),
                "reason": m.choice_reason,
            }
        )

    review = (
        db.query(ReviewSummary)
        .filter(ReviewSummary.candidate_id == tournament.winner_candidate_id)
        .first()
    )

    entry = DecisionJournalEntry(
        session_id=session.id,
        winner_candidate_id=tournament.winner_candidate_id,
        choice_log=choice_log,
        confidence=_compute_confidence(review),
        followup_due_at=datetime.now(timezone.utc) + FOLLOWUP_AFTER,
    )
    db.add(entry)
    session.engine_phase = "done"
    db.commit()
    db.refresh(entry)
    return entry


def get_journal_entry(db: Session, session: RequestSession) -> DecisionJournalEntry:
    entry = (
        db.query(DecisionJournalEntry)
        .filter(DecisionJournalEntry.session_id == session.id)
        .first()
    )
    if entry is None:
        raise HTTPException(status_code=404, detail="journal entry not found")
    return entry


def record_followup(
    db: Session, session: RequestSession, satisfaction: int
) -> DecisionJournalEntry:
    """6개월 후 만족도 재조사 응답을 기록하고 장기 만족도를 반영한다."""
    entry = get_journal_entry(db, session)
    if entry.followup_answered_at is not None:
        raise HTTPException(status_code=409, detail="followup already answered")

    entry.followup_satisfaction = satisfaction
    entry.followup_answered_at = datetime.now(timezone.utc)

    confidence = dict(entry.confidence)
    confidence["long_term"] = satisfaction * 20
    available = [
        v for k, v in confidence.items() if k != "overall" and v is not None
    ]
    confidence["overall"] = round(sum(available) / len(available)) if available else None
    entry.confidence = confidence

    db.commit()
    db.refresh(entry)
    return entry
