FROM postgres:17-alpine
RUN apk add --no-cache python3 py3-cryptography
COPY hms_backup.py /usr/local/bin/hms_backup.py
COPY hms-backup.sh hms-restore.sh hms-loop.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh
ENTRYPOINT ["/bin/sh", "/usr/local/bin/hms-loop.sh"]
