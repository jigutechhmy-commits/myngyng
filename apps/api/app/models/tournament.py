import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Tournament(Base):
    """CHOICE 단계의 월드컵 토너먼트 (PRD Phase 7)."""

    __tablename__ = "tournaments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("request_sessions.id"), index=True, unique=True
    )
    size: Mapped[int] = mapped_column(Integer)  # 2/4/8/16 (Auto는 생성 시 확정)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | done
    winner_candidate_id: Mapped[str | None] = mapped_column(
        ForeignKey("candidate_products.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TournamentMatch(Base):
    """토너먼트 개별 매치 (A vs B)."""

    __tablename__ = "tournament_matches"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tournament_id: Mapped[str] = mapped_column(ForeignKey("tournaments.id"), index=True)
    round_no: Mapped[int] = mapped_column(Integer)  # 1 = 첫 라운드
    match_no: Mapped[int] = mapped_column(Integer)  # 라운드 내 순번 (0부터)
    candidate_a_id: Mapped[str] = mapped_column(ForeignKey("candidate_products.id"))
    candidate_b_id: Mapped[str] = mapped_column(ForeignKey("candidate_products.id"))
    winner_candidate_id: Mapped[str | None] = mapped_column(
        ForeignKey("candidate_products.id"), nullable=True
    )
    # 사용자가 남긴 선택 이유 (PRD: AI는 정답을 강요하지 않고 이유를 기록한다)
    choice_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
