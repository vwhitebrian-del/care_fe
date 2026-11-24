@echo off
rem DANGER: replaces the live database with a backup. Takes a safety backup first.
rem Usage: restore.bat <file-name>   (example: restore.bat care-20261124-030000.dump.enc)
cd /d "%~dp0.."
if "%~1"=="" (echo الاستخدام: restore.bat ^<اسم-الملف^> & pause & exit /b 1)
echo تحذير: ستُستبدل قاعدة البيانات الحية بالنسخة: %~1
echo ستُؤخذ نسخة احتياطية للحالة الحالية قبل الاستبدال.
set /p CONFIRM=اكتب YES بالأحرف الكبيرة للمتابعة: 
if not "%CONFIRM%"=="YES" (echo أُلغيت العملية. & pause & exit /b 0)
docker compose stop backend celery-worker celery-beat web
docker compose exec -T backup /usr/local/bin/hms-restore.sh apply /backups/%~1
if errorlevel 1 (
  echo [خطأ] فشلت الاستعادة. النسخة الحالية محفوظة في مجلد backups قبل الاستبدال.
  docker compose up -d
  pause & exit /b 1
)
docker compose up -d
docker compose exec -T backend python manage.py migrate
echo تمت الاستعادة. راجع النظام قبل الاستخدام.
pause
