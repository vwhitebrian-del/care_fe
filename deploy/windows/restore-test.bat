@echo off
rem Tests a backup by restoring it into a scratch database. The live database is not touched.
rem Usage: restore-test.bat [file-name]   (default: the newest backup)
cd /d "%~dp0.."
set "FILE=%~1"
if "%FILE%"=="" (
  for /f "delims=" %%f in ('dir /b /o-d backups\care-*.dump.enc 2^>nul') do (set "FILE=%%f" & goto :found)
)
:found
if "%FILE%"=="" (echo [خطأ] لا توجد نسخ احتياطية في مجلد backups & pause & exit /b 1)
echo اختبار النسخة: %FILE%
docker compose exec -T backup /usr/local/bin/hms-restore.sh test /backups/%FILE%
if errorlevel 1 (echo [خطأ] فشل اختبار الاستعادة.) else (echo النسخة صالحة وقابلة للاستعادة.)
pause
