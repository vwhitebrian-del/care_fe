# تثبيت وتشغيل نظام مستشفى سويد على ويندوز (يُشغَّل مرة واحدة)
# الاستخدام: انقر يميناً على setup.bat > تشغيل كمسؤول (أو شغّل setup.bat فقط)
$ErrorActionPreference = "Stop"
$deploy = Split-Path -Parent $PSScriptRoot
Set-Location $deploy

function Say($m) { Write-Host "==> $m" -ForegroundColor Cyan }

# 1) Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Say "Docker غير مثبّت. جاري التثبيت عبر winget (قد يطلب إعادة تشغيل الجهاز)"
  winget install -e --id Docker.DockerDesktop --accept-package-agreements --accept-source-agreements
  Write-Host "بعد انتهاء التثبيت: أعد تشغيل الجهاز، افتح Docker Desktop مرة واحدة، ثم شغّل setup.bat من جديد." -ForegroundColor Yellow
  exit 0
}
try { docker info *> $null } catch { }
if ($LASTEXITCODE -ne 0) {
  Say "افتح Docker Desktop وانتظر حتى يصبح جاهزاً (أيقونة الحوت ثابتة) ثم شغّل setup.bat من جديد."
  exit 1
}

# 2) ملف الإعدادات مع كلمات مرور عشوائية
if (-not (Test-Path .env)) {
  Say "إنشاء ملف الإعدادات .env"
  function Rand($n) { -join ((48..57 + 65..90 + 97..122) | Get-Random -Count $n | ForEach-Object { [char]$_ }) }
  $lan = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*" -and $_.PrefixOrigin -ne "WellKnown" } | Select-Object -First 1).IPAddress
  if (-not $lan) { $lan = "localhost" }
  $dbpw = Rand 24
  $env = (Get-Content .env.example -Raw -Encoding UTF8)
  $env = $env.Replace("CHANGE_ME_DB", $dbpw).Replace("CHANGE_ME_LONG_RANDOM", (Rand 60)).Replace("CHANGE_ME_MINIO_USER", "minio" + (Rand 8)).Replace("CHANGE_ME_MINIO_PASS", (Rand 24)).Replace("192.168.1.10", $lan)
  [IO.File]::WriteAllText("$deploy\.env", $env, (New-Object Text.UTF8Encoding($false)))
  Say "عنوان الجهاز في الشبكة: $lan  (به تفتح النظام من التابلت)"
}

# 3) التشغيل
Say "بناء وتشغيل النظام (أول مرة تستغرق 10-20 دقيقة)"
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { Write-Host "فشل التشغيل. أرسل لي مخرجات: docker compose logs" -ForegroundColor Red; exit 1 }

Say "انتظار الخادم الخلفي"
$ok = $false
for ($i = 0; $i -lt 60; $i++) {
  try { $r = Invoke-WebRequest -UseBasicParsing http://localhost/api/v1/ping/ -TimeoutSec 3 -ErrorAction Stop; $ok = $true; break } catch {
    if ($_.Exception.Response -ne $null) { $ok = $true; break }
    Start-Sleep -Seconds 5 }
}
docker compose exec -T backend python manage.py migrate --noinput

# 4) مستخدم المدير
$marker = ".admin_created"
if (-not (Test-Path $marker)) {
  $pw = Read-Host "اختر كلمة مرور لمدير النظام (المستخدم: admin)"
  docker compose exec -T -e DJANGO_SUPERUSER_PASSWORD=$pw backend python manage.py createsuperuser --noinput --username admin --email admin@soued.local --phone_number +963947110110
  if ($LASTEXITCODE -eq 0) { New-Item $marker -ItemType File | Out-Null }
}

# 5) تهيئة المستشفى والأقسام (تُتخطّى إن وُجدت)
Say "إنشاء المستشفى والأقسام"
docker compose cp init_hospital.py backend:/tmp/init_hospital.py
docker compose exec -T backend python manage.py shell -c "exec(open('/tmp/init_hospital.py', encoding='utf-8').read())"

Say "جاهز! افتح http://localhost  (ومن التابلت: http://عنوان-الجهاز)"
Start-Process "http://localhost"
