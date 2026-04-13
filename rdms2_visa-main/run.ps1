# Django Development Server
# Gelistirme sunucusunu baslatir

Write-Host "Airline Management System - Sunucu Baslatiliyor..." -ForegroundColor Cyan
Write-Host ""

# Virtual environment aktivasyonu
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
    .\.venv\Scripts\Activate.ps1
    Write-Host "[OK] Virtual environment aktif" -ForegroundColor Green
} else {
    Write-Host "[HATA] Virtual environment bulunamadi!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Django development server baslatiliyor..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Erisim adresleri:" -ForegroundColor Yellow
Write-Host "   Ana Sayfa:    http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "   Admin Panel:  http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
Write-Host "[UYARI] Sunucuyu durdurmak icin Ctrl+C" -ForegroundColor Yellow
Write-Host ""

python manage.py runserver

