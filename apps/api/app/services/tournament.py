"""CHOICE 단계 — 토너먼트 생성/진행 (PRD Phase 7)."""

import random
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import (
    CandidateProduct,
    RequestSession,
    ReviewSummary,
    Tournament,
    TournamentMatch,
)
from app.services.engine import _require_phase, shortlisted_candidates


def _bracket_size(requested: int, available: int) -> int:
    """요청 규모와 가용 후보 수로 실제 브래킷 크기를 정한다 (2의 거듭제곱)."""
    if available < 2:
        raise HTTPException(status_code=409, detail="need at least 2 candidates for tournament")
    max_size = 1 << (available.bit_length() - 1)  # 가용 수 이하 최대 2^n
    if requested == 0:  # Auto
        return min(max_size, 16)
    return min(requested, max_size)


def create_tournament(db: Session, session: RequestSession) -> Tournament:
    _require_phase(session, "final_entry")
    if db.query(Tournament).filter(Tournament.session_id == session.id).first():
        raise HTTPException(status_code=409, detail="tournament already exists")

    candidates = shortlisted_candidates(db, session)
    size = _bracket_size(session.tournament_size, len(candidates))

    # 시드: 적합도+만족도 상위 N 진출, 대진은 무작위
    reviews = {
        r.candidate_id: r
        for r in db.query(ReviewSummary)
        .filter(ReviewSummary.candidate_id.in_([c.id for c in candidates]))
        .all()
    }

    def seed_score(c: CandidateProduct) -> int:
        review = reviews.get(c.id)
        return (review.fit_score + review.satisfaction_score) if review else 0

    entrants = sorted(candidates, key=seed_score, reverse=True)[:size]
    random.shuffle(entrants)

    tournament = Tournament(session_id=session.id, size=size)
    db.add(tournament)
    db.flush()

    for i in range(size // 2):
        db.add(
            TournamentMatch(
                tournament_id=tournament.id,
                round_no=1,
                match_no=i,
                candidate_a_id=entrants[2 * i].id,
                candidate_b_id=entrants[2 * i + 1].id,
            )
        )

    session.engine_phase = "choice"
    db.commit()
    db.refresh(tournament)
    return tournament


def get_tournament(db: Session, session: RequestSession) -> Tournament:
    tournament = db.query(Tournament).filter(Tournament.session_id == session.id).first()
    if tournament is None:
        raise HTTPException(status_code=404, detail="tournament not found")
    return tournament


def matches(db: Session, tournament: Tournament) -> list[TournamentMatch]:
    return (
        db.query(TournamentMatch)
        .filter(TournamentMatch.tournament_id == tournament.id)
        .order_by(TournamentMatch.round_no, TournamentMatch.match_no)
        .all()
    )


def choose_winner(
    db: Session,
    tournament: Tournament,
    match_id: str,
    winner_candidate_id: str,
    reason: str | None,
) -> Tournament:
    if tournament.status == "done":
        raise HTTPException(status_code=409, detail="tournament already finished")

    match = db.get(TournamentMatch, match_id)
    if match is None or match.tournament_id != tournament.id:
        raise HTTPException(status_code=404, detail="match not found")
    if match.winner_candidate_id is not None:
        raise HTTPException(status_code=409, detail="match already decided")
    if winner_candidate_id not in (match.candidate_a_id, match.candidate_b_id):
        raise HTTPException(status_code=422, detail="winner must be one of the match candidates")

    match.winner_candidate_id = winner_candidate_id
    match.choice_reason = reason
    match.decided_at = datetime.now(timezone.utc)

    # 현재 라운드가 끝났으면 다음 라운드 생성 또는 우승 확정
    current_round = [m for m in matches(db, tournament) if m.round_no == match.round_no]
    if all(m.winner_candidate_id for m in current_round):
        winners = [m.winner_candidate_id for m in current_round]
        if len(winners) == 1:
            tournament.status = "done"
            tournament.winner_candidate_id = winners[0]
        else:
            for i in range(len(winners) // 2):
                db.add(
                    TournamentMatch(
                        tournament_id=tournament.id,
                        round_no=match.round_no + 1,
                        match_no=i,
                        candidate_a_id=winners[2 * i],
                        candidate_b_id=winners[2 * i + 1],
                    )
                )

    db.commit()
    db.refresh(tournament)
    return tournament
