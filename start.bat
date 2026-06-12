@echo off
rem GOOD CHOICE one-click run (Windows)
setlocal enabledelayedexpansion
cd /d "%~dp0"

where docker >nul 2>nul
if errorlevel 1 (
  echo Docker가 설치되어 있지 않습니다.
  echo https://www.docker.com/products/docker-desktop/ 에서 설치 후 다시 실행해주세요.
  pause
  exit /b 1
)

docker info >nul 2>nul
if errorlevel 1 (
  echo Docker Desktop이 실행 중이지 않습니다.
  echo Docker Desktop을 먼저 실행한 뒤 다시 시도해주세요.
  pause
  exit /b 1
)

if not exist .env (
  copy .env.example .env >nul
  echo .env 파일을 생성했습니다. ANTHROPIC_API_KEY를 입력하면 실제 AI로 동작합니다.
)

set WEB_PORT=3000
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
  if "%%a"=="WEB_PORT" set WEB_PORT=%%b
)

echo GOOD CHOICE를 빌드/실행합니다. (처음 실행은 몇 분 정도 걸릴 수 있습니다)
docker compose up --build -d

echo 웹 서버가 준비될 때까지 기다리는 중...
set READY=0
for /l %%i in (1,1,150) do (
  if "!READY!"=="0" (
    curl -sf http://localhost:%WEB_PORT% >nul 2>nul
    if not errorlevel 1 (
      set READY=1
    ) else (
      timeout /t 2 >nul
    )
  )
)

if "%READY%"=="0" (
  echo 웹 서버가 아직 준비되지 않았습니다. 로그를 확인해주세요:
  docker compose logs --tail=50
  pause
  exit /b 1
)

echo.
echo 준비 완료! http://localhost:%WEB_PORT%/start
start http://localhost:%WEB_PORT%/start
pause
