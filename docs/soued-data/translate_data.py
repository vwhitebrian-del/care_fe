import psycopg
T_USERS={"admin":("مدير","النظام"),"care-admin":("طالب","سويد"),"care-doctor":("سامر","الخطيب"),"care-fac-admin":("فراس","المفتي"),"care-nurse":("رنا","حداد"),"care-role-admin":("ليث","درويش"),"care-role-manager":("هالة","شاهين"),"care-role-member":("بشار","علي"),"care-staff":("سلمى","ديب"),"care-volunteer":("عمار","نصور")}
S=[("Fasting Blood Glucose Test","تحليل سكر الدم الصيامي"),("Fasting Blood Glucose","سكر الدم الصيامي"),
("Complete Blood Count (CBC) Panel","صورة دم كاملة (CBC)"),("Complete Blood Count (CBC) Test","تحليل صورة دم كاملة (CBC)"),("Complete Blood Count","صورة دم كاملة"),
("Lipid Panel Observation","شحوم الدم"),("Lipid Panel Test","تحليل شحوم الدم"),("Lipid Panel Blood Specimen","عينة دم لشحوم الدم"),("Lipid Panel","شحوم الدم"),
("Urinalysis Observation","تحليل البول"),("Urinalysis Test","تحليل بول"),("Urinalysis Specimen","عينة بول"),("Urinalysis","تحليل البول"),
("Blood Glucose Test Specimen","عينة دم لسكر الدم"),("CBC Blood Specimen","عينة دم لصورة الدم"),
("Amoxicillin 500mg Capsule","أموكسيسيلين 500 ملغ كبسول"),("Paracetamol 500mg Tablet","باراسيتامول 500 ملغ أقراص"),("Ibuprofen 400mg Tablet","إيبوبروفين 400 ملغ أقراص"),("Pair of Gloves","زوج قفازات"),
("Amoxicillin","أموكسيسيلين"),("Paracetamol","باراسيتامول"),("Ibuprofen","إيبوبروفين"),("Gloves","قفازات"),
("Lab Tests","التحاليل المخبرية"),("Medications","الأدوية"),("Consumables","المستهلكات"),
("Pathology Lab","مخبر التحاليل"),("Main Pharmacy","الصيدلية الرئيسية"),("Bio-Chemistry Lab","مخبر الكيمياء الحيوية"),
("Default Availability","التوفر الافتراضي"),("Consultation Room 1","غرفة المعاينة 1"),("Default Queue","الطابور الافتراضي"),("General Consultation","معاينة عامة"),("Doctor Consultation Schedule","جدول معاينات الطبيب"),
("Initial Stock Request","طلب مخزون أولي"),("Initial Stock Delivery","تسليم مخزون أولي"),("Ward Top-up Request","طلب تعبئة الجناح"),("Ward Top-up Delivery","تسليم تعبئة الجناح"),
("Old Age Discount","خصم كبار السن"),("Child Discount","خصم الأطفال"),("IGST","ضريبة الخدمات"),("GST","ضريبة المبيعات")]
SUP=["مورّد الشرق للأدوية","مورّد الساحل الطبي","مورّد سورية للمستلزمات"]
NAMECOLS=[("emr_activitydefinition","title"),("emr_chargeitemdefinition","title"),("emr_chargeitem","title"),("emr_observationdefinition","title"),("emr_specimendefinition","title"),("emr_productknowledge","name"),("emr_resourcecategory","title"),("emr_healthcareservice","name"),("emr_facilitylocation","name"),("emr_availability","name"),("emr_tokensubqueue","name"),("emr_tokenqueue","name"),("emr_tokencategory","name"),("emr_schedule","name"),("emr_requestorder","name"),("emr_deliveryorder","name"),("emr_dispenseorder","name"),("emr_organization","name")]
ROLES={"Volunteer":"متطوع","Doctor":"طبيب","Staff":"موظف","Nurse":"ممرض","Administrator":"مدير","Facility Admin":"مدير المستشفى","Health Department":"مديرية الصحة"}
c=psycopg.connect("postgresql://postgres:postgres@localhost:5432/care");cur=c.cursor()
for u,(f,l) in T_USERS.items(): cur.execute("update users_user set first_name=%s,last_name=%s where username=%s",(f,l,u))
cur.execute("select distinct name from emr_organization where name like 'Supplier %%' order by 1"); sup=[r[0] for r in cur.fetchall()]
for i,s in enumerate(sup): 
    for t,col in [("emr_organization","name"),("emr_requestorder","name"),("emr_deliveryorder","name")]:
        cur.execute(f"update {t} set {col}=replace({col},%s,%s)",(s,SUP[i%3]))
for a,b in ROLES.items(): cur.execute("update emr_organization set name=%s where name=%s and org_type='role'",(b,a))
for t,col in NAMECOLS:
    for a,b in S: cur.execute(f"update {t} set {col}=replace({col},%s,%s) where {col} like %s",(a,b,f"%{a}%"))
# json display values
cur.execute("select table_name,column_name from information_schema.columns where table_schema='public' and data_type='jsonb' and table_name like 'emr_%%' and table_name not in ('emr_valueset','emr_questionnaire','emr_template')")
for t,col in cur.fetchall():
    for a,b in S[-4:]:
        cur.execute(f"update {t} set {col}=replace({col}::text,%s,%s)::jsonb where {col}::text like %s",(f'"display": "{a}"',f'"display": "{b}"',f'%"display": "{a}"%'))
        cur.execute(f"update {t} set {col}=replace({col}::text,%s,%s)::jsonb where {col}::text like %s",(f'"display":"{a}"',f'"display":"{b}"',f'%"display":"{a}"%'))
c.commit();print("ok")
