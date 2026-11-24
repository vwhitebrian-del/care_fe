# تشغيل نظام مستشفى سويد على سيرفر المستشفى (Docker)

المتطلبات: سيرفر Linux عليه Docker وDocker Compose، ويُفضَّل 4 GB ذاكرة فأكثر.

```bash
cd deploy
cp .env.example .env      # عدّل كلمات المرور وعنوان السيرفر (BUCKET_EXTERNAL_ENDPOINT)
docker compose up -d --build
docker compose exec backend python manage.py migrate         # (يجري تلقائياً عند أول تشغيل في بعض الإصدارات)
docker compose exec backend python manage.py createsuperuser
```

ثم افتح `http://<عنوان السيرفر>` من أي جهاز في الشبكة (الحاسوب أو التابلت).

- **النسخ الاحتياطي:** يومياً 03:00 إلى `deploy/backups/` (يحتفظ بآخر 14 يوماً). للاستعادة:
  `gunzip -c backups/care-AAAAMMDD-HHMM.sql.gz | docker compose exec -T db psql -U care care`
- **التحديث:** `git pull && docker compose up -d --build`
- **الملفات والصور:** مخزّنة في مجلد `minio-data`؛ انسخه ضمن النسخ الاحتياطي الخارجي أيضاً.
- يُنصح بنسخ مجلد `backups/` إلى قرص خارجي أو جهاز آخر.

> تحذير: `load_fixtures` لا يعمل في وضع الإنتاج عمداً. للبيانات التجريبية استخدم بيئة التطوير (docs/soued-data).
