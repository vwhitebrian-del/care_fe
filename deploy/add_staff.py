"""إضافة موظفين من ملف staff.csv (آمن للتكرار: يتخطى من له اسم دخول موجود).

الأعمدة: الدور، الاسم، اسم الدخول، كلمة السر، القسم (اختياري)، الجنس (اختياري)، الهاتف (اختياري)
الأدوار: طبيب، ممرض، محاسب، استقبال، صيدلي، موظف، مدير
"""
import csv
import sys

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from care.emr.models.organization import FacilityOrganization, Organization
from care.facility.models.facility import Facility
from care.fixtures.base import CareFixtureBase

PATH = sys.argv[1] if len(sys.argv) > 1 else "/tmp/staff.csv"
ROLE_MAP = {  # الدور بالعربي: (اسم الدور في النظام، اسم منظمة الدور)
    "طبيب": ("Doctor", "طبيب"), "ممرض": ("Nurse", "ممرض"), "ممرضة": ("Nurse", "ممرض"),
    "محاسب": ("Staff", "موظف"), "استقبال": ("Staff", "موظف"), "موظف": ("Staff", "موظف"),
    "صيدلي": ("Pharmacist", "صيدلي"), "مدير": ("Facility Admin", "مدير المستشفى"),
}

User = get_user_model()
su = User.objects.filter(is_superuser=True).first()
client = APIClient()
client.force_authenticate(user=su)
base = CareFixtureBase(client)
base.user = su
roles = base.get_roles()
fac = Facility.objects.first()
latakia = Organization.objects.get(name="اللاذقية", org_type="govt")


def read_rows(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "cp1256"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    return list(csv.DictReader(text.splitlines()))


def next_phone():
    n = User.objects.count()
    while True:
        p = f"+9639000{n:05d}"
        if not User.objects.filter(phone_number=p).exists():
            return p
        n += 1


added = skipped = failed = 0
for row in read_rows(PATH):
    row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
    role_ar, name, username, pw = row.get("الدور", ""), row.get("الاسم", ""), row.get("اسم الدخول", ""), row.get("كلمة السر", "")
    if not (role_ar and name and username and pw):
        continue
    if role_ar not in ROLE_MAP:
        print(f"✗ {username}: دور غير معروف «{role_ar}»")
        failed += 1
        continue
    import re
    if not re.fullmatch(r"[A-Za-z0-9_-]+", username):
        print(f"✗ {username}: اسم الدخول يقبل فقط حروفاً إنكليزية وأرقاماً و - و _ (بلا نقطة أو مسافة)")
        failed += 1
        continue
    if User.objects.filter(username=username).exists():
        print(f"- {username}: موجود مسبقاً (تم التخطي)")
        skipped += 1
        continue
    role_name, org_name = ROLE_MAP[role_ar]
    role_org = Organization.objects.get(name=org_name, org_type="role")
    first, _, last = name.partition(" ")
    gender = "female" if row.get("الجنس", "") in ("أنثى", "انثى", "female") else "male"
    try:
        u = base.create_user(
            latakia.external_id, username=username, email=f"{username}@soued.local", password=pw,
            first_name=first, last_name=last or "-", gender=gender,
            phone_number=row.get("الهاتف") or next_phone(),
            role_orgs=[{"organization": str(role_org.external_id), "role": str(roles[role_name].id)}],
        )
        dept = row.get("القسم", "")
        if dept:
            fo = FacilityOrganization.objects.filter(facility=fac, name=dept).first()
            if fo:
                base.add_user_to_facility_organization(str(fac.external_id), str(fo.external_id), u["id"], str(roles[role_name].id))
            else:
                print(f"! {username}: القسم «{dept}» غير موجود، أُنشئ المستخدم بلا قسم")
        print(f"✓ {username} ({role_ar})")
        added += 1
    except Exception as e:
        print(f"✗ {username}: {str(e)[:200]}")
        failed += 1
print(f"تمت الإضافة: {added} | متخطى: {skipped} | فشل: {failed}")
