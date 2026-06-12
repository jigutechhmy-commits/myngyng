from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import categories, sessions

app = FastAPI(
    title="GOOD CHOICE API",
    description="Good Choice Engine - AI 의사결정 엔진 기반 구매 월드컵 서비스",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router, prefix="/api/categories", tags=["categories"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
