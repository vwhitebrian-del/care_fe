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

## النسخ الاحتياطي والاستعادة (مشفّر AES-256-GCM)

- **مفتاح التشفير:** يُنشأ تلقائياً في `deploy\secrets\backup.key` عند `setup.bat`. **انسخه إلى فلاشة أو مكان آمن خارج الجهاز فوراً.** بدونه لا تُستعاد أي نسخة.
- **نسخة يومية تلقائية:** الساعة 03:00، ويُحتفظ بها 14 يوماً (قابل للتغيير بـ `BACKUP_KEEP_DAYS`).
- **كل نسخة تُتحقق منها فوراً** بعد الإنشاء، فإن فشل التحقق لا تُعتبر النسخة صالحة.
- `backup-now.bat`: نسخة فورية.
- `restore-test.bat [اسم-الملف]`: يستعيد النسخة في قاعدة تجريبية ويفحصها، دون لمس البيانات الحية. استخدمه دورياً.
- `restore.bat <اسم-الملف>`: يستبدل قاعدة البيانات الحية بالنسخة بعد طلب كتابة `YES`، ويأخذ نسخة للحالة الحالية أولاً.
- يُحفظ كل ملف نسخة في `deploy\backups` باسم `care-YYYYMMDD-HHMMSS.dump.enc`.
