@echo off
rem Shows service state and the latest backups.
cd /d "%~dp0.."
docker compose ps
echo.
echo آخر النسخ الاحتياطية:
dir /b /o-d backups 2>nul | more +0
pause
