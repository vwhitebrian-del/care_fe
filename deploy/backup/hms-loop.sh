#!/bin/sh
# Runs an encrypted backup every BACKUP_EVERY_HOURS hours (default 4), starting now.
INTERVAL=$(( ${BACKUP_EVERY_HOURS:-4} * 3600 ))
LAST=0
while true; do
  NOW=$(date +%s)
  if [ $((NOW - LAST)) -ge "$INTERVAL" ]; then
    LAST=$NOW
    /usr/local/bin/hms-backup.sh || echo "backup FAILED at $(date)"
  fi
  sleep 60
done
