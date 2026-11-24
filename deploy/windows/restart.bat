@echo off
rem Restarts the CARE services. Takes a backup first; aborts if the backup fails.
cd /d "%~dp0"
call _backup-before-change.bat
if "%BACKUP_OK%"=="0" goto :end
cd /d "%~dp0.."
docker compose restart backend celery-worker celery-beat web
docker compose ps
echo تمت إعادة التشغيل.
:end
pause
