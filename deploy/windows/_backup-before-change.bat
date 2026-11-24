@echo off
rem Takes an encrypted, verified backup. Sets BACKUP_OK=1 on success, 0 on failure.
cd /d "%~dp0.."
docker compose exec -T backup /usr/local/bin/hms-backup.sh
if errorlevel 1 (
  set BACKUP_OK=0
  echo [خطأ] فشلت النسخة الاحتياطية. أُلغيت العملية.
) else (
  set BACKUP_OK=1
)
