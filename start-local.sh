#!/usr/bin/env bash
# GOOD CHOICE 원클릭 실행 - Docker 없이 (Mac/Linux)
# 필요: python3, node/npm, PostgreSQL(+pgvector)
set -uo pipefail
cd "$(dirname "$0")"
ROOT="$(pwd)"
RUN_DIR="$ROOT/.run"
mkdir -p "$RUN_DIR"

API_PORT=8000
WEB_PORT=3000
if [ -f .env ]; then
  v=$(grep -E '^WEB_PORT=' .env 2>/dev/null | tail -1 | cut -d= -f2); [ -n "${v:-}" ] && WEB_PORT="$v"
  v=$(grep -E '^API_PORT=' .env 2>/dev/null | tail -1 | cut -d= -f2); [ -n "${v:-}" ] && API_PORT="$v"
fi

need() { command -v "$1" >/dev/null 2>&1; }

echo "[1/6] 필수 프로그램 확인 중..."
MISSING=()
need python3 || MISSING+=("python3")
need node || MISSING+=("node")
need npm || MISSING+=("npm")
need psql || MISSING+=("postgresql")
need pg_isready || MISSING+=("postgresql")

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "다음 프로그램이 설치되어 있지 않습니다: ${MISSING[*]}"
  if [[ "$(uname)" == "Darwin" ]]; then
    echo "  brew install python node postgresql@16 pgvector"
    echo "  brew services start postgresql@16"
  else
    echo "  sudo apt install -y python3 python3-venv nodejs npm postgresql postgresql-16-pgvector"
    echo "  sudo service postgresql start"
  fi
  echo "설치 후 이 스크립트를 다시 실행해주세요."
  exit 1
fi

echo "[2/6] PostgreSQL 확인 중..."
if ! pg_isready -q 2>/dev/null; then
  echo "PostgreSQL이 꺼져 있어 시작을 시도합니다..."
  if [[ "$(uname)" == "Darwin" ]] && need brew; then
    brew services start postgresql@16 >/dev/null 2>&1 || brew services start postgresql >/dev/null 2>&1 || true
  else
    sudo service postgresql start >/dev/null 2>&1 || sudo pg_ctlcluster 16 main start >/dev/null 2>&1 || true
  fi
  for _ in $(seq 1 15); do pg_isready -q 2>/dev/null && break; sleep 1; done
fi

if ! pg_isready -q 2>/dev/null; then
  echo "PostgreSQL을 시작하지 못했습니다. 직접 실행한 뒤 다시 시도해주세요."
  exit 1
fi

echo "[3/6] DB/계정 준비 중..."
PG_RUNNER=""
if psql -d postgres -tAc "select 1" >/dev/null 2>&1; then
  PG_RUNNER="psql -d postgres"
elif psql -U postgres -d postgres -tAc "select 1" >/dev/null 2>&1; then
  PG_RUNNER="psql -U postgres -d postgres"
elif command -v sudo >/dev/null 2>&1 && sudo -u postgres psql -tAc "select 1" >/dev/null 2>&1; then
  PG_RUNNER="sudo -u postgres psql"
fi

if [ -z "$PG_RUNNER" ]; then
  echo "PostgreSQL 관리자 권한으로 접속하지 못했습니다."
  echo "  sudo -u postgres psql -c \"select 1\" 으로 접속 가능한지 확인 후 다시 시도해주세요."
  exit 1
fi

$PG_RUNNER -tAc "SELECT 1 FROM pg_roles WHERE rolname='goodchoice'" 2>/dev/null | grep -q 1 \
  || $PG_RUNNER -c "CREATE USER goodchoice WITH PASSWORD 'goodchoice';" >/dev/null 2>&1

$PG_RUNNER -tAc "SELECT 1 FROM pg_database WHERE datname='goodchoice'" 2>/dev/null | grep -q 1 \
  || $PG_RUNNER -c "CREATE DATABASE goodchoice OWNER goodchoice;" >/dev/null 2>&1

if ! $PG_RUNNER -tAc "SELECT 1 FROM pg_available_extensions WHERE name='vector'" 2>/dev/null | grep -q 1; then
  echo "pgvector 확장이 설치되어 있지 않습니다."
  if [[ "$(uname)" == "Darwin" ]]; then
    echo "  brew install pgvector"
  else
    echo "  sudo apt install -y postgresql-16-pgvector"
  fi
  exit 1
fi

echo "[4/6] API 서버 준비 중... (처음 실행은 시간이 걸릴 수 있습니다)"
cd "$ROOT/apps/api"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -q -e ".[dev]"
[ -f .env ] || cp .env.example .env
.venv/bin/alembic upgrade head
.venv/bin/python scripts/seed_categories.py
nohup .venv/bin/uvicorn app.main:app --port "$API_PORT" > "$RUN_DIR/api.log" 2>&1 &
echo $! > "$RUN_DIR/api.pid"
cd "$ROOT"

echo "[5/6] 웹 서버 준비 중... (처음 실행은 시간이 걸릴 수 있습니다)"
cd "$ROOT/apps/web"
if [ "$API_PORT" != "8000" ]; then
  echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:$API_PORT" > .env.local
elif [ ! -f .env.local ]; then
  cp .env.example .env.local
fi
[ -d node_modules ] || npm install
nohup npm run dev -- -p "$WEB_PORT" > "$RUN_DIR/web.log" 2>&1 &
echo $! > "$RUN_DIR/web.pid"
cd "$ROOT"

echo "[6/6] 웹 서버가 준비될 때까지 대기 중..."
READY=0
for _ in $(seq 1 120); do
  if curl -sf "http://localhost:$WEB_PORT" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 2
done

if [ "$READY" -ne 1 ]; then
  echo "웹 서버가 아직 준비되지 않았습니다. 로그를 확인해주세요:"
  echo "  $RUN_DIR/api.log"
  echo "  $RUN_DIR/web.log"
  exit 1
fi

URL="http://localhost:$WEB_PORT/start"
echo ""
echo "준비 완료! $URL"
echo "(종료하려면 stop-local.sh 또는 stop-local.command 실행)"

if need open; then
  open "$URL"
elif need xdg-open; then
  xdg-open "$URL"
else
  echo "브라우저에서 위 주소를 직접 열어주세요."
fi
