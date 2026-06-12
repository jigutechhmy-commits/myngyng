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

### 가장 쉬운 실행 방법 (Docker 한 번에 실행)

[Docker Desktop](https://www.docker.com/products/docker-desktop/)만 설치되어 있으면 됩니다.

1. 터미널에서 이 저장소 폴더로 이동
2. API 키 설정 (선택, 없으면 Mock 데이터로 동작):
   ```bash
   cp .env.example .env
   # .env 파일을 열어 ANTHROPIC_API_KEY=발급받은키 입력
   ```
3. 전체 실행:
   ```bash
   docker compose up --build
   ```
4. 브라우저에서 **http://localhost:3000/start** 접속 → STEP1~5 입력부터 시작

종료는 `Ctrl+C`, 컨테이너/볼륨까지 정리하려면 `docker compose down -v`.

### 개발 환경 실행 (직접 구동)
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
