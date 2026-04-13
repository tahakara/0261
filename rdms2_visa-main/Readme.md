# Airline Management System 🛫

Django ve PostgreSQL kullanılarak geliştirilmiş havayolu yönetim sistemi.

## 📋 Proje Hakkında

Bu proje, havayolu operasyonlarını yönetmek için geliştirilmiş bir web uygulamasıdır. Uçak filosu yönetimi, yolcu bilgileri, uçuş planlaması ve rezervasyon işlemlerini kapsar.

## 🗂️ Veritabanı Yapısı

Sistem aşağıdaki ana varlıklardan oluşmaktadır:

### 1. **Aircraft (Uçaklar)**
- Filo yönetimi
- Uçak özellikleri (kapasite, menzil)
- Durum takibi (aktif, bakımda, tamir)

### 2. **Passengers (Yolcular)**
- Yolcu bilgileri
- Benzersiz yolcu numarası
- İletişim bilgileri (telefon, adres)

### 3. **Flights (Uçuşlar)**
- Uçuş planlaması
- Kalkış/Varış noktaları
- Uçak atamaları
- Durum takibi

### 4. **Flight Bookings (Rezervasyonlar)**
- Yolcu-uçuş ilişkileri
- Koltuk atamaları
- Rezervasyon durumları

## 🛠️ Teknolojiler

- **Backend:** Django (Python)
- **Database:** PostgreSQL
- **Virtual Environment:** venv (`.venv` klasöründe)
- **Version Control:** Git

## � Hızlı Başlangıç

Projeyi hızlıca çalıştırmak için:

```powershell
# 1. Virtual environment'ı aktif et
.\.venv\Scripts\Activate.ps1

# 2. Kurulum scriptini çalıştır (ilk kurulum için)
.\setup.ps1

# 3. Sunucuyu başlat
.\run.ps1
# veya
python manage.py runserver
```

Tarayıcınızda [http://127.0.0.1:8000](http://127.0.0.1:8000) adresine gidin.

## �📦 Kurulum

### 1. Virtual Environment Aktivasyonu

```powershell
# PowerShell
.\.venv\Scripts\Activate.ps1
```

### 2. Gerekli Paketlerin Yüklenmesi

```powershell
pip install django psycopg2-binary python-dotenv
```

### 3. Environment Değişkenleri

`.env` dosyası proje kök dizininde mevcuttur. Gerekli değişkenler:

```env
# Django Settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=aviation_sys
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=your-host
DB_PORT=5432
```

### 4. Veritabanı Oluşturma

PostgreSQL'de veritabanını oluşturun:

```sql
CREATE DATABASE aviation_sys;
```

Veritabanı şemasını yükleyin:

```powershell
psql -U postgres -d aviation_sys -f Database\Database_Postgres\airline_database_schema.sql
```

### 5. Django Projesi Başlatma

```powershell
# Django projesi oluştur
django-admin startproject airline_system .

# Django modellerini oluştur (inspectdb ile mevcut DB'den)
python manage.py inspectdb > models.py

# Migrations
python manage.py makemigrations
python manage.py migrate

# Admin kullanıcı oluştur
python manage.py createsuperuser

# Sunucuyu başlat
python manage.py runserver
```

## 📁 Proje Yapısı

```
VTYS/
├── .venv/                                 # Virtual environment
├── airline_system/                        # Django proje klasörü
│   ├── __init__.py
│   ├── settings.py                        # Proje ayarları
│   ├── urls.py                            # Ana URL yönlendirmeleri
│   ├── wsgi.py
│   └── asgi.py
├── flights/                               # Django app (ana uygulama)
│   ├── migrations/                        # Veritabanı migration'ları
│   ├── templates/flights/                 # HTML template'leri
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── aircraft_list.html
│   │   ├── aircraft_detail.html
│   │   ├── flight_list.html
│   │   ├── flight_detail.html
│   │   ├── passenger_list.html
│   │   ├── passenger_detail.html
│   │   └── booking_list.html
│   ├── __init__.py
│   ├── admin.py                           # Admin panel konfigürasyonu
│   ├── apps.py                            # App konfigürasyonu
│   ├── models.py                          # Veritabanı modelleri
│   ├── tests.py                           # Test dosyaları
│   ├── urls.py                            # App URL'leri
│   └── views.py                           # View fonksiyonları
├── Database/
│   ├── Database_Postgres/
│   │   ├── airline_database_schema.sql    # DB şeması
│   │   ├── airline_sample_data.sql        # Örnek veriler
│   │   └── airline_queries.sql            # SQL sorguları
│   └── Database_MySQL/                    # MySQL alternatifi
├── manage.py                              # Django yönetim scripti
├── requirements.txt                       # Python paket bağımlılıkları
├── setup.ps1                              # Kurulum scripti
├── run.ps1                                # Sunucu başlatma scripti
├── .env                                   # Environment değişkenleri
├── .gitignore                             # Git ignore dosyası
└── README.md                              # Bu dosya
```

## 🗃️ Veritabanı Varlıkları (Entities)

### Aircraft (Uçaklar)
- `aircraft_id` (UUID, PK)
- `code_number` (Unique)
- `brand`, `model`
- `passenger_capacity`, `range_km`
- `is_active`, `status`

### Passengers (Yolcular)
- `passenger_id` (UUID, PK)
- `passenger_number` (Unique)
- `first_name`, `last_name`

### Passenger Phones (Yolcu Telefonları)
- `phone_id` (UUID, PK)
- `passenger_id` (FK)
- `phone_type` (home/mobile/work)
- `phone_number`
- `is_primary`

### Passenger Addresses (Yolcu Adresleri)
- `address_id` (UUID, PK)
- `passenger_id` (FK)
- `address_type` (home/work/billing/other)
- `address_line`, `city`, `country`, `postal_code`
- `is_primary`

### Flights (Uçuşlar)
- `flight_id` (UUID, PK)
- `flight_number` (Unique)
- `departure_point`, `arrival_point`
- `flight_date`, `flight_time`
- `aircraft_id` (FK)
- `status`

### Flight Bookings (Rezervasyonlar)
- `booking_id` (UUID, PK)
- `flight_id` (FK)
- `passenger_id` (FK)
- `seat_number`
- `booking_status`
- `booking_date`

## 🔍 Özellikler

- ✅ UUID tabanlı benzersiz tanımlayıcılar
- ✅ Otomatik zaman damgası (created_at, updated_at)
- ✅ Veri bütünlüğü için constraint'ler
- ✅ İlişkisel veri yapısı (One-to-Many, Many-to-Many)
- ✅ Performans için indexler
- ✅ Cascade silme desteği
- ✅ Enum-like status alanları

## 👨‍💻 Geliştirme

```powershell
# Virtual environment'ı aktif et
.\.venv\Scripts\Activate.ps1

# Geliştirme sunucusunu başlat
python manage.py runserver

# Yeni migration oluştur
python manage.py makemigrations

# Migration'ları uygula
python manage.py migrate

# Test çalıştır
python manage.py test

# Admin kullanıcı oluştur
python manage.py createsuperuser
```

## 🌐 URL Endpoints

### Ana Sayfa
- `/` - Ana sayfa (dashboard)

### Uçak Yönetimi
- `/aircraft/` - Tüm uçakları listele
- `/aircraft/<uuid>/` - Uçak detayı

### Yolcu Yönetimi
- `/passengers/` - Tüm yolcuları listele
- `/passengers/<uuid>/` - Yolcu detayı

### Uçuş Yönetimi
- `/flights/` - Tüm uçuşları listele
- `/flights/<uuid>/` - Uçuş detayı

### Rezervasyon Yönetimi
- `/bookings/` - Tüm rezervasyonları listele

### Admin Panel
- `/admin/` - Django admin paneli

## 🧪 Test

Testleri çalıştırmak için:

```powershell
# Tüm testleri çalıştır
python manage.py test

# Belirli bir app'i test et
python manage.py test flights

# Verbose output ile test et
python manage.py test --verbosity=2
```

## 👤 Admin Panel

Django admin paneline erişmek için önce bir superuser oluşturun:

```powershell
python manage.py createsuperuser
```

Ardından tarayıcınızda [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) adresine gidin.

Admin panelinde şunları yapabilirsiniz:
- ✅ Uçak ekleme, düzenleme, silme
- ✅ Yolcu yönetimi (telefon ve adres bilgileri ile)
- ✅ Uçuş planlama ve düzenleme
- ✅ Rezervasyon yönetimi
- ✅ Filtreleme ve arama özellikleri
- ✅ İstatistiksel görünümler

## 📝 Notlar

- Veritabanı şeması `Database\Database_Postgres\airline_database_schema.sql` dosyasında tanımlıdır
- Environment değişkenleri `.env` dosyasında saklanır (Git'e eklenmez)
- Virtual environment `.venv` klasöründedir

## 📄 Lisans

Bu proje eğitim amaçlı geliştirilmiştir.