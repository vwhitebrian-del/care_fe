# -*- coding: utf-8 -*-
"""Builds questionnaires.json (CARE questionnaire specs) for مستشفى سويد.
Run: python build_questionnaires.py  -> writes questionnaires.json next to this file.
"""
import json, os, uuid

NS = uuid.UUID("6f1c2a52-8e7d-4b1e-9a3c-2d5e7f9a1b00")


def q(link, text, typ="string", req=False, opts=None, children=None, desc=None):
    d = {"link_id": link, "text": text, "type": typ, "required": req,
         "answer_constraint": "required" if req else "optional"}
    if opts:
        d["answer_option"] = [{"value": o} for o in opts]
    if children is not None:
        d["questions"] = children
    if desc:
        d["description"] = desc
    return d


def build_all(title_prefix):
    T = []
    T.append(("clinic-visit", "زيارة عيادة", [
        q("chief-complaint", "الشكوى الرئيسية", "text", True),
        q("history", "التاريخ المرضي", "text"),
        q("exam", "الفحص السريري", "text"),
        q("diagnosis", "التشخيص", "text", True),
        q("plan", "الخطة العلاجية", "text"),
        q("prescriptions", "الوصفات", "text"),
        q("follow-up-date", "موعد المتابعة", "date"),
    ]))
    T.append(("chronic-followup", "متابعة ضغط وسكري", [
        q("bp-systolic", "الضغط الانقباضي (ملم زئبق)", "integer"),
        q("bp-diastolic", "الضغط الانبساطي (ملم زئبق)", "integer"),
        q("fasting-glucose", "السكر الصائم (ملغ/دل)", "decimal"),
        q("random-glucose", "السكر العشوائي (ملغ/دل)", "decimal"),
        q("weight", "الوزن (كغ)", "decimal"),
        q("current-meds", "الأدوية الحالية", "text"),
        q("symptoms", "الأعراض الجديدة", "text"),
        q("notes", "ملاحظات", "text"),
    ]))
    T.append(("patient-instructions", "تعليمات المريض", [
        q("instructions", "التعليمات", "text", True),
        q("warning-signs", "علامات تستوجب العودة فوراً", "text", True),
        q("next-visit", "موعد المراجعة", "date"),
    ]))
    T.append(("er-exam", "فحص الطوارئ", [
        q("arrival-time", "وقت الوصول", "dateTime", True),
        q("arrival-mode", "طريقة الوصول", "choice", True,
          ["مشياً", "إسعاف", "نقل خاص", "أخرى"]),
        q("chief-complaint", "الشكوى الرئيسية", "text", True),
        q("bp", "الضغط (ملم زئبق)", "string"),
        q("pulse", "النبض (نبضة/دقيقة)", "integer"),
        q("resp-rate", "معدل التنفس (نفس/دقيقة)", "integer"),
        q("temperature", "الحرارة (°م)", "decimal"),
        q("spo2", "تشبع الأكسجين (%)", "integer"),
        q("consciousness", "مستوى الوعي", "choice", True,
          ["واعٍ", "يستجيب للكلام", "يستجيب للألم", "فاقد الاستجابة"]),
        q("triage", "تصنيف الفرز", "choice", True,
          ["حرج", "عاجل", "متوسط", "غير عاجل"]),
        q("initial-exam", "الفحص الأولي", "text"),
        q("immediate-actions", "الإجراءات المبدئية", "text"),
        q("disposition", "القرار النهائي", "choice", True,
          ["خروج", "تنويم", "تحويل"]),
    ]))
    T.append(("ecg-report", "تخطيط القلب", [
        q("indication", "سبب الطلب", "text"),
        q("rhythm", "الإيقاع", "string"),
        q("heart-rate", "معدل القلب (نبضة/دقيقة)", "integer"),
        q("axis", "المحور", "string"),
        q("pr", "فترة PR (ms)", "integer"),
        q("qrs", "عرض QRS (ms)", "integer"),
        q("qt", "فترة QT (ms)", "integer"),
        q("st-changes", "تغيرات قطعة ST", "text"),
        q("t-changes", "تغيرات الموجة T", "text"),
        q("conclusion", "الاستنتاج", "text", True),
        q("recommendation", "التوصية", "text"),
    ]))
    T.append(("admission", "قبول التنويم", [
        q("admission-reason", "سبب الدخول", "text", True),
        q("history-brief", "التاريخ المرضي المختصر", "text"),
        q("allergies", "الحساسية", "text", True),
        q("current-meds", "الأدوية الحالية", "text"),
        q("department", "القسم", "string", True),
        q("bed", "السرير", "string", True),
    ]))
    T.append(("nursing-note", "ملاحظة تمريض (نوبة)", [
        q("vitals", "العلامات الحيوية", "text"),
        q("meds-given", "الأدوية المعطاة", "text"),
        q("changes", "التغيرات", "text"),
        q("handover", "تعليمات للنوبة التالية", "text"),
    ]))
    T.append(("shift-handover", "تسليم مناوبة", [
        q("condition", "الحالة الحالية", "text", True),
        q("ongoing", "الإجراءات الجارية", "text"),
        q("pending", "المهام المعلّقة", "text"),
        q("urgent-followup", "متابعة عاجلة", "text"),
    ]))
    T.append(("medication-administration", "جدول إعطاء الأدوية", [
        q("drug", "الدواء", "string", True),
        q("dose", "الجرعة", "string", True),
        q("route", "طريقة الإعطاء", "choice", True,
          ["فموي", "وريدي", "عضلي", "تحت الجلد", "موضعي", "أخرى"]),
        q("time-given", "وقت الإعطاء", "dateTime", True),
        q("given-by", "المُعطي", "string", True),
    ]))
    T.append(("operation-report", "تقرير عملية", [
        q("procedure", "نوع العملية", "text", True),
        q("date", "التاريخ", "date", True),
        q("surgeon", "الجراح", "string", True),
        q("anesthesiologist", "المخدِّر", "string"),
        q("duration-min", "المدة (دقيقة)", "integer"),
        q("procedure-details", "وصف الإجراء", "text", True),
        q("complications", "المضاعفات", "text"),
        q("post-op-recommendations", "التوصيات بعد العملية", "text"),
    ]))
    T.append(("consent", "موافقة على إجراء", [
        q("procedure-explained", "الإجراء الذي تم شرحه", "text", True),
        q("risks-explained", "المخاطر التي تم شرحها", "text", True),
        q("consent-given", "أوافق على الإجراء", "boolean", True),
        q("signer-name", "اسم الموقّع", "string", True),
        q("signer-relation", "صفة الموقّع", "choice", True,
          ["المريض نفسه", "الوليّ", "الوصي"]),
    ]))
    T.append(("post-op-followup", "متابعة ما بعد العملية", [
        q("pain-score", "الألم (من 10)", "integer"),
        q("bleeding", "النزيف", "choice", False, ["لا يوجد", "قليل", "متوسط", "شديد"]),
        q("wound", "الجرح", "text"),
        q("medications", "الأدوية", "text"),
        q("warning-signs", "علامات تستوجب العودة فوراً", "text", True),
    ]))
    T.append(("discharge-summary", "ملخص الخروج", [
        q("discharge-diagnosis", "التشخيص عند الخروج", "text", True),
        q("course", "ما أُجري خلال الإقامة", "text", True),
        q("discharge-meds", "الأدوية عند الخروج", "text"),
        q("follow-up", "المتابعة", "text"),
    ]))
    T.append(("labor-delivery", "مخاض وولادة", [
        q("labor-duration", "مدة المخاض (ساعة)", "decimal"),
        q("stages", "المراحل", "text"),
        q("fetal-indicators", "المؤشرات الجنينية", "text"),
        q("delivery-method", "طريقة الولادة", "choice", True,
          ["طبيعية", "قيصرية", "أداتية"]),
        q("complications", "المضاعفات", "text"),
    ]))
    T.append(("newborn-assessment", "حديثو الولادة", [
        q("weight-g", "الوزن (غرام)", "integer"),
        q("apgar-1", "APGAR دقيقة 1", "integer"),
        q("apgar-5", "APGAR دقيقة 5", "integer"),
        q("initial-exam", "الفحص الأولي", "text"),
        q("vaccinations", "التطعيمات", "text"),
        q("follow-up", "المتابعة", "text"),
    ]))
    T.append(("lab-imaging-request", "طلب فحوص مخبرية وأشعة", [
        q("test-type", "نوع الفحص", "choice", True, ["مخبري", "أشعة", "أخرى"]),
        q("test-name", "اسم الفحص", "string", True),
        q("clinical-reason", "السبب السريري", "text", True),
        q("priority", "الأولوية", "choice", True, ["عاجل", "عادي"]),
    ]))
    out = []
    for slug, title, questions in T:
        out.append({"slug": slug, "title": title_prefix + title, "questions": questions})
    return out


def assign_ids(spec):
    """Deterministic UUIDs so re-running the loader is idempotent."""
    def walk(items, prefix):
        for it in items:
            it["id"] = str(uuid.uuid5(NS, f"{prefix}/{it['link_id']}"))
            if it.get("questions"):
                walk(it["questions"], f"{prefix}/{it['link_id']}")
    walk(spec["questions"], spec["slug"])
    return spec


if __name__ == "__main__":
    specs = [assign_ids(s) for s in build_all("")]
    for s in specs:
        s.update({"status": "active", "description": "", "styling_metadata": {}})
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "questionnaires.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(specs, f, ensure_ascii=False, indent=2)
    print(len(specs), "templates ->", out)
