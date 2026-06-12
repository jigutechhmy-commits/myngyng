#!/usr/bin/env bash
# GOOD CHOICE 원클릭 실행 (Mac/Linux)
set -euo pipefail
cd "$(dirname "$0")"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker가 설치되어 있지 않습니다."
  echo "https://www.docker.com/products/docker-desktop/ 에서 설치 후 다시 실행해주세요."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  echo "Docker Desktop이 실행 중이지 않습니다."
  echo "Docker Desktop을 먼저 실행한 뒤 다시 시도해주세요."
  exit 1
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env 파일을 생성했습니다. ANTHROPIC_API_KEY를 입력하면 실제 AI로 동작합니다 (비워두면 Mock 데이터로 동작)."
fi

WEB_PORT=3000
if grep -qE '^WEB_PORT=' .env; then
  WEB_PORT=$(grep -E '^WEB_PORT=' .env | tail -1 | cut -d= -f2)
fi

echo "GOOD CHOICE를 빌드/실행합니다. (처음 실행은 몇 분 정도 걸릴 수 있습니다)"
docker compose up --build -d

echo "웹 서버가 준비될 때까지 기다리는 중..."
READY=0
for _ in $(seq 1 150); do
  if curl -sf "http://localhost:${WEB_PORT}" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 2
done

if [ "$READY" -ne 1 ]; then
  echo "웹 서버가 아직 준비되지 않았습니다. 로그를 확인해주세요:"
  docker compose logs --tail=50
  exit 1
fi

URL="http://localhost:${WEB_PORT}/start"
echo ""
echo "준비 완료! $URL"

if command -v open >/dev/null 2>&1; then
  open "$URL"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$URL"
else
  echo "브라우저에서 위 주소를 직접 열어주세요."
fi
