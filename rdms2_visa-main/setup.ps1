# Airline Management System - Baslangic Scripti
# Bu script projeyi ilk kurulum icin hazirlar

Write-Host "Airline Management System - Baslatiliyor..." -ForegroundColor Cyan
Write-Host ""

# Virtual environment kontrolu
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "[OK] Virtual environment bulundu" -ForegroundColor Green
    .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "[HATA] Virtual environment bulunamadi!" -ForegroundColor Red
    Write-Host "Once 'python -m venv .venv' komutunu calistirin." -ForegroundColor Yellow
    exit 1
}

# Paket kontrolu
Write-Host ""
Write-Host "Django kurulumu kontrol ediliyor..." -ForegroundColor Cyan
try {
    python -c "import django" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Django kurulu" -ForegroundColor Green
    } else {
        throw "Django kurulu degil"
    }
} catch {
    Write-Host "[UYARI] Django kurulu degil, paketler yukleniyor..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# .env dosyasi kontrolu
Write-Host ""
Write-Host "Environment dosyasi kontrol ediliyor..." -ForegroundColor Cyan
if (Test-Path ".env") {
    Write-Host "[OK] .env dosyasi bulundu" -ForegroundColor Green
} else {
    Write-Host "[HATA] .env dosyasi bulunamadi!" -ForegroundColor Red
    if (Test-Path ".env.example") {
        Write-Host "[UYARI] .env.example dosyasini .env olarak kopyalayin ve duzenleyin." -ForegroundColor Yellow
    }
    exit 1
}

# Migration kontrolu
Write-Host ""
Write-Host "Veritabani migrations kontrol ediliyor..." -ForegroundColor Cyan
$migrations = Get-ChildItem -Path "flights\migrations" -Filter "*.py" -Recurse | Where-Object { $_.Name -ne "__init__.py" }
if ($migrations.Count -eq 0) {
    Write-Host "[UYARI] Migration dosyalari bulunamadi, olusturuluyor..." -ForegroundColor Yellow
    python manage.py makemigrations
}

Write-Host ""
Write-Host "Migrations uygulanıyor..." -ForegroundColor Cyan
python manage.py migrate

# Superuser kontrolu
Write-Host ""
Write-Host "Admin kullanicisi olusturulsun mu? (Y/N)" -ForegroundColor Cyan
$createUser = Read-Host
if ($createUser -eq "Y" -or $createUser -eq "y") {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "[BASARILI] Kurulum tamamlandi!" -ForegroundColor Green
Write-Host ""
Write-Host "Sunucuyu baslatmak icin:" -ForegroundColor Cyan
Write-Host "   python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Erisim adresleri:" -ForegroundColor Cyan
Write-Host "   Ana Sayfa: http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "   Admin Panel: http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""

