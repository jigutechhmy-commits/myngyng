import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DecisionNarrative(Base):
    """DIGGING 단계의 제품 세계관 조사 결과 (PRD Phase 5)."""

    __tablename__ = "decision_narratives"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidate_products.id"), index=True, unique=True
    )
    # Decision Narrative 한 줄 (예: "공구를 만들겠다는 IBM 철학의 후계자")
    narrative: Mapped[str] = mapped_column(String(300))
    # 세계관 서술 (탄생 배경/철학/팬덤/역사 등)
    story: Mapped[str] = mapped_column(Text)
    # Digging Score: 철학/역사성/팬덤/독창성/커뮤니티평가/스토리성 각 0~10
    digging_scores: Mapped[dict] = mapped_column(JSON, default=dict)
    # Fact Shield: 출처 목록 + AI 추론 여부 표시
    sources: Mapped[list] = mapped_column(JSON, default=list)
    ai_inferred: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
