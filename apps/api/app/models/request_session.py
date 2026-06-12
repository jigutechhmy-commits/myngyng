import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RequestSession(Base):
    """사용자 입력 세션 (PRD STEP 1~5)."""

    __tablename__ = "request_sessions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"))

    # STEP 2. 예산
    budget: Mapped[int] = mapped_column(Integer)  # 원 단위
    budget_tolerance_pct: Mapped[int] = mapped_column(Integer, default=10)

    # STEP 3. 용도 (자연어)
    usage_text: Mapped[str] = mapped_column(String(2000))

    # STEP 4. 우선순위 (1~3순위)
    priorities: Mapped[list] = mapped_column(JSON, default=list)

    # STEP 5. 토너먼트 규모: 2 | 4 | 8 | 16 | 0(Auto)
    tournament_size: Mapped[int] = mapped_column(Integer, default=0)

    # 엔진 진행 상태: created → plan → research → review_scan → list_up
    #               → digging → final_entry → choice → done
    engine_phase: Mapped[str] = mapped_column(String(20), default="created")

    # Phase 1. PLAN 결과 (최적 사양서)
    spec_sheet: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
