#!/usr/bin/env bash
# GOOD CHOICE 종료 - Docker 없이 (Mac/Linux)
cd "$(dirname "$0")"

pkill -f "uvicorn app.main:app" 2>/dev/null && echo "API 서버 종료"
pkill -f "next-server" 2>/dev/null && echo "웹 서버 종료"
pkill -f "next dev" 2>/dev/null

rm -f .run/api.pid .run/web.pid
echo "완료"
