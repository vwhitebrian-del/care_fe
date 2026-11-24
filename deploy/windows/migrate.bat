@echo off
rem Upgrades the database schema (migrations). Takes a backup first; aborts if the backup fails.
cd /d "%~dp0"
call _backup-before-change.bat
if "%BACKUP_OK%"=="0" goto :end
cd /d "%~dp0.."
docker compose exec -T backend python manage.py migrate
if errorlevel 1 (
  echo [خطأ] فشلت ترقية البنية. النسخة الاحتياطية السابقة محفوظة في مجلد backups.
) else (
  echo تمت ترقية بنية القاعدة بنجاح.
)
:end
pause
