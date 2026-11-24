@echo off
rem Creates an encrypted, verified backup now.
cd /d "%~dp0.."
docker compose exec -T backup /usr/local/bin/hms-backup.sh
if errorlevel 1 (echo [خطأ] فشلت النسخة الاحتياطية.) else (echo تم حفظ النسخة مشفّرة في مجلد backups.)
pause
