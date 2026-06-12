@echo off
rem GOOD CHOICE one-click run without Docker (Windows)
setlocal enabledelayedexpansion
cd /d "%~dp0"

set API_PORT=8000
set WEB_PORT=3000
if exist .env (
  for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if "%%a"=="WEB_PORT" set WEB_PORT=%%b
    if "%%a"=="API_PORT" set API_PORT=%%b
  )
)

where python >nul 2>nul
if errorlevel 1 (
  echo Python이 필요합니다: https://www.python.org/downloads/
  pause
  exit /b 1
)
where node >nul 2>nul
if errorlevel 1 (
  echo Node.js가 필요합니다: https://nodejs.org/
  pause
  exit /b 1
)
where psql >nul 2>nul
if errorlevel 1 (
  echo PostgreSQL이 필요합니다: https://www.postgresql.org/download/windows/
  echo  ^(설치 시 Stack Builder로 pgvector 확장도 추가해주세요^)
  pause
  exit /b 1
)

echo [1/4] DB 준비 중... ^(postgres 비밀번호를 물으면 입력해주세요^)
psql -U postgres -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='goodchoice'" | findstr "1" >nul
if errorlevel 1 psql -U postgres -d postgres -c "CREATE USER goodchoice WITH PASSWORD 'goodchoice';"
psql -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='goodchoice'" | findstr "1" >nul
if errorlevel 1 psql -U postgres -d postgres -c "CREATE DATABASE goodchoice OWNER goodchoice;"

echo [2/4] API 서버 준비 중... ^(처음 실행은 시간이 걸릴 수 있습니다^)
cd apps\api
if not exist .venv python -m venv .venv
call .venv\Scripts\pip install -q -e ".[dev]"
if not exist .env copy .env.example .env >nul
call .venv\Scripts\alembic upgrade head
call .venv\Scripts\python scripts\seed_categories.py
start "GOOD CHOICE API" cmd /k ".venv\Scripts\uvicorn app.main:app --port %API_PORT%"
cd ..\..

echo [3/4] 웹 서버 준비 중... ^(처음 실행은 시간이 걸릴 수 있습니다^)
cd apps\web
if not "%API_PORT%"=="8000" (
  echo NEXT_PUBLIC_API_BASE_URL=http://localhost:%API_PORT% > .env.local
) else (
  if not exist .env.local copy .env.example .env.local >nul
)
if not exist node_modules npm install
start "GOOD CHOICE WEB" cmd /k "npm run dev -- -p %WEB_PORT%"
cd ..\..

echo [4/4] 웹 서버가 준비될 때까지 대기 중...
set READY=0
for /l %%i in (1,1,120) do (
  if "!READY!"=="0" (
    curl -sf http://localhost:%WEB_PORT% >nul 2>nul
    if not errorlevel 1 (
      set READY=1
    ) else (
      timeout /t 2 >nul
    )
  )
)

echo.
echo 준비 완료! http://localhost:%WEB_PORT%/start
start http://localhost:%WEB_PORT%/start
echo ^(종료하려면 새로 열린 API/WEB 창을 닫거나 stop-local.bat 실행^)
pause
