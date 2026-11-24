#!/bin/sh
# Creates an encrypted backup in /backups, verifies it, then applies retention.
set -eu
OUT=/backups
KEY=/secrets/backup.key
KEEP_DAYS=${KEEP_DAYS:-14}
[ -f "$KEY" ] || { echo "[خطأ] مفتاح التشفير غير موجود: $KEY"; exit 1; }
mkdir -p "$OUT"
TS=$(date +%Y%m%d-%H%M%S)
F="$OUT/care-$TS.dump.enc"
TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT
pg_dump -Fc --no-owner -f "$TMP"
python3 /usr/local/bin/hms_backup.py encrypt "$TMP" "$F" "$KEY" >/dev/null
python3 /usr/local/bin/hms_backup.py verify "$F" "$KEY"
find "$OUT" -name 'care-*.dump.enc*' -mtime +"$KEEP_DAYS" -delete
echo "backup ok: $F"
