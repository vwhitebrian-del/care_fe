# -*- coding: utf-8 -*-
"""Loads the hospital's questionnaire templates into CARE. Idempotent (skips existing slugs).
Run inside the backend via:
  manage.py shell -c "exec(open('/app/init_templates.py', encoding='utf-8').read())"
"""
import json, os
from care.emr.models.questionnaire import Questionnaire
from care.emr.resources.questionnaire.spec import QuestionnaireCreateSpec
from care.facility.models import Facility

FACILITY_NAME = "مستشفى سويد"
PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "questionnaires.json")

facility = Facility.objects.filter(name=FACILITY_NAME).first()
if facility is None:
    raise SystemExit("facility not found; run init_hospital.py first")

specs = json.load(open(PATH, encoding="utf-8"))
created, skipped = 0, 0
for s in specs:
    exists = Questionnaire.objects.filter(
        slug=s["slug"], facility=facility, auth_context="facility", deleted=False
    ).exists()
    if exists:
        skipped += 1
        continue
    payload = {**s, "auth_context": "facility", "facility": str(facility.external_id),
               "subject_type": "encounter"}
    spec = QuestionnaireCreateSpec(**payload)
    obj = spec.de_serialize()
    obj.version = "1.0"
    obj.save()
    created += 1
print(f"templates: created={created} skipped={skipped}")
