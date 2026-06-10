import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FinalEntryCard(Base):
    """FINAL ENTRY 단계의 최종 카드 (PRD Phase 6)."""

    __tablename__ = "final_entry_cards"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_products.id"), index=True, unique=True
    )
    # 패키징 문구 (카드 헤드라인)
    headline: Mapped[str] = mapped_column(String(200))
    key_specs: Mapped[list] = mapped_column(JSON, default=list)  # 핵심 사양 요약
    pros: Mapped[list] = mapped_column(JSON, default=list)  # 장점
    cons: Mapped[list] = mapped_column(JSON, default=list)  # 단점
    review_digest: Mapped[str] = mapped_column(Text)  # 후기 요약
    worldview: Mapped[str] = mapped_column(Text)  # 세계관 (Decision Narrative 요약)
    recommended_for: Mapped[list] = mapped_column(JSON, default=list)  # 추천 대상
    not_recommended_for: Mapped[list] = mapped_column(JSON, default=list)  # 비추천 대상

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
