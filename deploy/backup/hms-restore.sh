#!/bin/sh
# Usage:
#   hms-restore.sh test  /backups/<file>.dump.enc   restore into a scratch DB and check it, then drop it
#   hms-restore.sh apply /backups/<file>.dump.enc   replace the live database (services must be stopped)
set -eu
MODE=${1:-}
F=${2:-}
KEY=/secrets/backup.key
case "$MODE" in test|apply) ;; *) echo "الاستخدام: hms-restore.sh test|apply <ملف>"; exit 2;; esac
[ -f "$F" ] || { echo "[خطأ] الملف غير موجود: $F"; exit 1; }
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
echo "1/4 فك التشفير والتحقق من التوقيع..."
python3 /usr/local/bin/hms_backup.py decrypt "$F" "$TMP" "$KEY" >/dev/null
echo "2/4 التحقق من أرشيف pg_dump..."
pg_restore --list "$TMP" >/dev/null
if [ "$MODE" = "test" ]; then
  DB=care_restore_test
  psql -d postgres -qc "DROP DATABASE IF EXISTS $DB WITH (FORCE)"
  psql -d postgres -qc "CREATE DATABASE $DB"
  echo "3/4 الاستعادة إلى قاعدة تجريبية..."
  pg_restore --no-owner --exit-on-error -d "$DB" "$TMP"
  echo "4/4 فحص المحتوى..."
  TBL=$(psql -d "$DB" -tAc "select count(*) from information_schema.tables where table_schema='public'")
  MIG=$(psql -d "$DB" -tAc "select count(*) from django_migrations")
  psql -d postgres -qc "DROP DATABASE $DB WITH (FORCE)"
  [ "$TBL" -gt 0 ] && [ "$MIG" -gt 0 ] || { echo "[خطأ] فحص المحتوى فشل"; exit 1; }
  echo "اختبار الاستعادة ناجح: جداول=$TBL، ترحيلات=$MIG"
else
  DB=$PGDATABASE
  echo "0/4 نسخة احتياطية للحالة الحالية قبل الاستبدال..."
  /usr/local/bin/hms-backup.sh
  psql -d postgres -qc "DROP DATABASE IF EXISTS \"$DB\" WITH (FORCE)"
  psql -d postgres -qc "CREATE DATABASE \"$DB\""
  echo "3/4 استعادة قاعدة البيانات الحية..."
  pg_restore --no-owner --exit-on-error -d "$DB" "$TMP"
  echo "4/4 تمت الاستعادة. شغّل ترقية البنية (migrate.bat) إن لزم."
fi
