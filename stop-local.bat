@echo off
rem GOOD CHOICE stop without Docker (Windows)
taskkill /FI "WINDOWTITLE eq GOOD CHOICE API*" /T /F >nul 2>nul
taskkill /FI "WINDOWTITLE eq GOOD CHOICE WEB*" /T /F >nul 2>nul
echo 완료
pause
