# myngyng
jigutech code factory

## GOOD CHOICE
AI 의사결정 엔진 기반 구매 월드컵 서비스

- PRD: [`docs/PRD_v1.md`](./docs/PRD_v1.md)
- 작업 계획: [`docs/PLAN.md`](./docs/PLAN.md)

### 구조
```
apps/web         # Next.js + Tailwind + shadcn/ui
apps/api         # FastAPI (Good Choice Engine)
packages/shared  # 카테고리 스펙 등 공통 정의
```

### 개발 환경 실행
```bash
# DB (PostgreSQL 16 + pgvector)
npm run db:up          # docker compose up -d db

# API
cd apps/api
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/python scripts/seed_categories.py
.venv/bin/uvicorn app.main:app --reload --port 8000

# Web
cd apps/web
cp .env.example .env.local
npm install && npm run dev   # http://localhost:3000
```
