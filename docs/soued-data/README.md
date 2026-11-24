# بيانات مستشفى سويد التجريبية (للخادم الخلفي ohcnetwork/care)

ترتيب التشغيل من مجلد الخادم الخلفي (بعد `migrate`):

1. `manage.py load_fixtures --path soued_fixtures.py` — المستشفى والأقسام والمرضى
2. `python seed_clinical.py` — وصفات وإعطاء أدوية وتقارير (يحتاج `PYTHONPATH=$PWD`)
3. `python translate_data.py` — تعريب أسماء الخدمات والأدوية والمستخدمين والخصومات
