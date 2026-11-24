@echo off
rem Takes a timestamped database backup. Sets BACKUP_OK=1 on success, 0 on failure.
cd /d "%~dp0.."
if not exist backups mkdir backups
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd-HHmmss"') do set TS=%%i
set BACKUP_FILE=backups\pre-change-%TS%.dump
docker compose exec -T db sh -c "pg_dump -U $POSTGRES_USER -Fc --no-owner $POSTGRES_DB > /tmp/hms.dump" && docker compose cp db:/tmp/hms.dump "%BACKUP_FILE%"
if errorlevel 1 (
  set BACKUP_OK=0
  echo [خطأ] فشل أخذ النسخة الاحتياطية. أُلغيت العملية.
) else (
  set BACKUP_OK=1
  echo نسخة احتياطية محفوظة: %BACKUP_FILE%
)
