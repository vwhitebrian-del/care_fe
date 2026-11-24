@echo off
chcp 65001 >nul
cd /d "%~dp0.."
docker compose cp staff.csv backend:/tmp/staff.csv
docker compose cp add_staff.py backend:/tmp/add_staff.py
docker compose exec -T backend python manage.py shell -c "import sys; sys.argv=['x','/tmp/staff.csv']; exec(open('/tmp/add_staff.py', encoding='utf-8').read())"
pause
