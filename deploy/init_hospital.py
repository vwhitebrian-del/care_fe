"""التهيئة الأولية لمستشفى سويد: المستشفى + الأقسام + المواقع (آمنة للتشغيل في الإنتاج).

التشغيل (من مجلد deploy): انظر setup.ps1 — النسخ إلى الحاوية ثم تنفيذه بـ manage.py shell
لا تغيّر كلمات المرور ولا تحذف شيئاً، ويمكن إعادة تشغيلها (تتخطى الموجود).
"""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient

from care.emr.models.organization import FacilityOrganization, Organization
from care.emr.models.location import FacilityLocation
from care.facility.models.facility import Facility
from care.fixtures.base import CareFixtureBase

HOSPITAL = {
    "name": "مستشفى سويد",
    "description": "مستشفى سويد الخاص — اللاذقية. رقم الترخيص 7435",
    "address": "اللاذقية — دوار الأزهري",
    "phone_number": "+963947110110",
    "pincode": 100000,
    "latitude": 35.5200,
    "longitude": 35.7900,
}

# (القسم، [الأقسام الفرعية])
DEPARTMENTS = [
    ("الإدارة والخدمات", [
        "الإدارة", "الاستقبال والقبول", "المحاسبة والفوترة", "الأرشيف الطبي والسجلات",
        "الموارد البشرية", "تقنية المعلومات", "الصيانة والخدمات", "التعقيم", "التمريض والإشراف",
    ]),
    ("الإسعاف والطوارئ", []),
    ("الطب الباطني", [
        "القلبية", "الهضمية", "الصدرية", "الكلية", "الغدد الصم", "العصبية", "الدم", "الروماتيزم",
    ]),
    ("الجراحة العامة", []),
    ("العظمية", []),
    ("النسائية والتوليد", []),
    ("الأطفال وحديثي الولادة", []),
    ("البولية", []),
    ("الأذنية والأنف والحنجرة", []),
    ("العينية", []),
    ("الجلدية", []),
    ("النفسية", []),
    ("العناية المشددة", []),
    ("غرف العمليات والإنعاش", []),
    ("المخبر", []),
    ("الأشعة", []),
    ("الفحوص الوظيفية (تخطيط القلب والإيكو)", []),
    ("بنك الدم", []),
    ("الصيدلية", []),
    ("التنويم", []),
]

# هيكل المواقع: مبنى > طوابق > غرف/أجنحة > أسرّة. (الاسم، النوع، القسم، [الأبناء] أو عدد الأسرّة)
# النوع: lvl طابق، wa جناح/قسم، ro غرفة، bd سرير. كل شيء قابل للتوسعة لاحقاً من الواجهة.
def beds(n):
    return [(f"سرير {i}", "bd", None, None) for i in range(1, n + 1)]

def room(num, n, dept):
    return (f"غرفة {num}", "ro", dept, beds(n))

TREE = [
    ("الطابق الأرضي", "lvl", "الإسعاف والطوارئ", [
        ("الإسعاف", "wa", "الإسعاف والطوارئ", beds(2)),
        ("العناية المشددة", "wa", "العناية المشددة", beds(4)),
    ]),
    ("الطابق الأول", "lvl", "التنويم", [
        ("تنويم الطابق الأول", "wa", "التنويم", [room(105, 1, "التنويم"), room(106, 1, "التنويم")]),
    ]),
    ("الطابق الثاني", "lvl", "التنويم", [
        ("تنويم الطابق الثاني", "wa", "التنويم", [room(n, 1, "التنويم") for n in (202, 203, 204, 205, 206, 207)]
            + [("جناح 211", "ro", "التنويم", beds(1)), ("جناح 212", "ro", "التنويم", beds(1))]),
    ]),
    ("الطابق الثالث", "lvl", "غرف العمليات والإنعاش", [
        (f"غرفة عمليات جراحية {i}", "ro", "غرف العمليات والإنعاش", []) for i in (1, 2, 3)
    ]),
    ("الطابق الرابع", "lvl", "القلبية", [
        ("عناية إكليلية", "wa", "القلبية", beds(4)),
        ("عناية قلبية", "wa", "القلبية", beds(4)),
        room(401, 2, "القلبية"),
        room(402, 2, "القلبية"),
        ("غرفة عمليات قلبية", "ro", "غرف العمليات والإنعاش", []),
        ("غرفة قثطرة قلبية", "ro", "القلبية", []),
    ]),
    ("المخبر", "wa", "المخبر", []),
    ("قسم الأشعة", "wa", "الأشعة", []),
    ("الصيدلية", "wa", "الصيدلية", []),
]

call_command("sync_permissions_roles")
call_command("sync_valueset")

su = get_user_model().objects.filter(is_superuser=True).first()
assert su, "أنشئ مدير النظام أولاً (createsuperuser)"
client = APIClient()
client.force_authenticate(user=su)
base = CareFixtureBase(client)
base.user = su

def get_geo(name, parent=None):
    q = Organization.objects.filter(name=name, org_type="govt")
    if q.exists():
        return q.first()
    kw = {"parent": parent.external_id} if parent else {}
    r = base.create_organization(org_type="govt", name=name, **kw)
    return Organization.objects.get(external_id=r["id"])

syria = get_geo("سوريا")
latakia = get_geo("اللاذقية", syria)

fac = Facility.objects.filter(name=HOSPITAL["name"]).first()
if fac is None:
    r = base.create_facility(
        latakia.external_id, facility_type="Private Hospital", is_public=False, features=[], **HOSPITAL
    )
    fac = Facility.objects.get(external_id=r["id"])
    print("أُنشئ المستشفى:", fac.name)
fid = str(fac.external_id)

existing = {o.name: o for o in FacilityOrganization.objects.filter(facility=fac)}
depts = {}
for name, children in DEPARTMENTS:
    if name in existing:
        parent = existing[name]
    else:
        r = base.create_facility_organization(fid, name=name, org_type="dept", description="")
        parent = FacilityOrganization.objects.get(external_id=r["id"])
        existing[name] = parent
    depts[name] = parent
    for ch in children:
        if ch not in existing:
            r = base.create_facility_organization(fid, name=ch, org_type="dept", description="", parent=str(parent.external_id))
            existing[ch] = FacilityOrganization.objects.get(external_id=r["id"])
print("الأقسام:", FacilityOrganization.objects.filter(facility=fac, org_type="dept").count())

def ensure(name, form, dept, parent_obj, parent_id):
    q = FacilityLocation.objects.filter(facility=fac, name=name, parent=parent_obj)
    if q.exists():
        return q.first()
    kw = {"parent": parent_id} if parent_id else {}
    mode = "instance" if form == "bd" else "kind"
    org = [str(depts[dept].external_id)] if dept in depts else []
    r = base.create_location(fid, name=name, description="", form=form, mode=mode, organizations=org, **kw)
    return FacilityLocation.objects.get(external_id=r["id"])

def build(items, parent_obj=None, parent_dept=None):
    for name, form, dept, kids in items:
        dept = dept or parent_dept
        obj = ensure(name, form, dept, parent_obj, str(parent_obj.external_id) if parent_obj else None)
        if kids:
            build(kids, obj, dept)

build(TREE)
print("المواقع:", FacilityLocation.objects.filter(facility=fac).count(),
      "| الأسرّة:", FacilityLocation.objects.filter(facility=fac, form="bd").count())
print("تمت التهيئة.")
