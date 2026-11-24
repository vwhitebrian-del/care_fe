@echo off
rem Copies new encrypted backups to Google Drive (via Google Drive for Desktop).
rem Only *.enc and *.sha256 files are copied; keys and .env are never copied here.
rem Usage: copy-to-drive.bat [destination]   (default: G:\My Drive\soued-backups)
cd /d "%~dp0.."
set "DST=%~1"
if "%DST%"=="" set "DST=G:\My Drive\soued-backups"
if not exist "%DST%" mkdir "%DST%" 2>nul
if not exist "%DST%" (echo [خطأ] المجلد غير متاح: %DST%. تأكد أن Google Drive for Desktop يعمل. & pause & exit /b 1)
robocopy "backups" "%DST%" *.enc *.sha256 /XO /R:2 /W:5 /NP /NFL /NDL
if errorlevel 8 (echo [خطأ] فشل النسخ إلى Google Drive. & pause & exit /b 1)
echo تم نسخ النسخ الجديدة إلى: %DST%
pause
