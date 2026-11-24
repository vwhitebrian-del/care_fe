cd /d "%~dp0.."
if not exist backups mkdir backups
docker compose exec -T db sh -c "pg_dump -U $POSTGRES_USER --no-owner $POSTGRES_DB | gzip" > backups\manual-backup.sql.gz
echo Backup saved in deploy\backups
pause
