#!/bin/sh
# نسخة احتياطية يومية الساعة 03:00 (توقيت دمشق) مع حذف الأقدم من KEEP_DAYS يوماً.
mkdir -p /backups
while true; do
  now=$(date +%H%M)
  if [ "$now" = "0300" ]; then
    f="/backups/care-$(date +%Y%m%d-%H%M).sql.gz"
    pg_dump --no-owner | gzip > "$f" && echo "backup ok: $f" || echo "backup FAILED"
    find /backups -name 'care-*.sql.gz' -mtime +"$KEEP_DAYS" -delete
    sleep 70
  fi
  sleep 30
done
