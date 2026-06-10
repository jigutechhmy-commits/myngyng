import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CandidateProduct(Base):
    """RESEARCH 단계에서 수집된 후보 제품 (PRD Phase 2)."""

    __tablename__ = "candidate_products"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    session_id: Mapped[str] = mapped_column(ForeignKey("request_sessions.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    brand: Mapped[str] = mapped_column(String(100))
    price: Mapped[int] = mapped_column(Integer)  # 원
    specs: Mapped[dict] = mapped_column(JSON, default=dict)
    # 데이터 출처: "ai"(AI 추정) | "search"(검색 API) | "crawl"(크롤러)
    source: Mapped[str] = mapped_column(String(20), default="ai")
    # LIST UP 단계 상태: "candidate" | "eliminated" | "shortlisted"
    status: Mapped[str] = mapped_column(String(20), default="candidate")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
