from datetime import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Category(Base):
    """카테고리별 사양 스키마 정의 (PRD STEP 1)."""

    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # 예: "laptop"
    name_ko: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(default=False)
    # 사양 필드 정의: [{key, label_ko, type, unit?, required?}, ...]
    spec_schema: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
