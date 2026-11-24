import django,datetime as dt
django.setup()
from model_bakery import baker
from django.utils import timezone
from care.emr.models import Encounter, Patient
from care.emr.models.medication_request import MedicationRequest, MedicationRequestPrescription
from care.emr.models.medication_administration import MedicationAdministration
from care.emr.models.service_request import ServiceRequest
from care.emr.models.diagnostic_report import DiagnosticReport
from care.users.models import User
now=timezone.now()
u=User.objects.get(username="care-doctor")
def cd(display,code): return {"display":display,"code":code,"system":"http://snomed.info/sct"}
meds=[("باراسيتامول 500 ملغ","161"),("أموكسيسيلين 500 ملغ","723"),("أوميبرازول 20 ملغ","7646")]
for enc in Encounter.objects.select_related("patient","facility").all()[:3]:
    pres=baker.make(MedicationRequestPrescription,encounter=enc,patient=enc.patient,status="active",name="وصفة طبية",prescribed_by=u)
    for i,(n,c) in enumerate(meds):
        dose={"type":"ordered","dose_quantity":{"value":1,"unit":cd("قرص","tablet")}}
        di=[{"sequence":1,"as_needed_boolean":False,"timing":{"repeat":{"frequency":3-i%2,"period":1,"period_unit":"d"}},"route":cd("فموي","26643006"),"dose_and_rate":dose,"patient_instruction":"بعد الطعام"}]
        mr=baker.make(MedicationRequest,patient=enc.patient,encounter=enc,status="active",intent="order",category="inpatient",priority="routine",do_not_perform=False,medication=cd(n,c),dosage_instruction=di,authored_on=now,requester=u,prescription=pres)
        baker.make(MedicationAdministration,patient=enc.patient,encounter=enc,request=mr,status="completed",category="inpatient",medication=cd(n,c),occurrence_period_start=now-dt.timedelta(hours=2+i),authored_on=now,recorded=now,performer=[],dosage={"text":"قرص واحد","route":cd("فموي","26643006")})
    sr=baker.make(ServiceRequest,title="تحليل دم شامل CBC",patient=enc.patient,facility=enc.facility,encounter=enc,status="completed",intent="order",priority="routine",category="laboratory")
    baker.make(DiagnosticReport,status="final",category={"display":"Laboratory","code":"LAB","system":"http://terminology.hl7.org/CodeSystem/v2-0074"},service_request=sr,patient=enc.patient,encounter=enc,facility=enc.facility)
print("done",MedicationRequest.objects.count(),DiagnosticReport.objects.count())
