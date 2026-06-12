import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DecisionJournalEntry(Base):
    """사용자의 최종 선택 기록 (PRD 5장 Decision Journal + 6장 Choice Confidence)."""

    __tablename__ = "decision_journal_entries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(
        ForeignKey("request_sessions.id"), index=True, unique=True
    )
    winner_candidate_id: Mapped[str] = mapped_column(ForeignKey("candidate_products.id"))
    # 라운드별 선택 이유 모음: [{round_label, picked, over, reason}]
    choice_log: Mapped[list] = mapped_column(JSON, default=list)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Choice Confidence (0~100): fit/budget/review/long_term(초기 null)/overall
    confidence: Mapped[dict] = mapped_column(JSON, default=dict)

    # 6개월 후 만족도 재조사
    followup_due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    followup_satisfaction: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1~5
    followup_answered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
