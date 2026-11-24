#!/bin/sh
# Runs the encrypted backup every day at 03:00 (Asia/Damascus, set via TZ).
while true; do
  if [ "$(date +%H%M)" = "0300" ]; then
    /usr/local/bin/hms-backup.sh || echo "backup FAILED"
    sleep 70
  fi
  sleep 30
done
