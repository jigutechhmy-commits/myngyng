import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ReviewSummary(Base):
    """REVIEW SCAN 단계의 후보별 후기 요약/평가 (PRD Phase 3)."""

    __tablename__ = "review_summaries"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_products.id"), index=True, unique=True
    )
    summary: Mapped[str] = mapped_column(Text)
    # 출처 링크/이름 목록 (Fact Shield: MVP는 AI 생성 출처 표기)
    sources: Mapped[list] = mapped_column(JSON, default=list)

    # 각 1~5점 (PRD Phase 3 평가 항목)
    fit_score: Mapped[int] = mapped_column(Integer)  # 요구사항 적합도
    budget_score: Mapped[int] = mapped_column(Integer)  # 예산 적합도
    satisfaction_score: Mapped[int] = mapped_column(Integer)  # 만족도

    # LIST UP 자동 탈락 판단 재료 (PRD Phase 4)
    missing_required: Mapped[bool] = mapped_column(Boolean, default=False)
    critical_flaw: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
