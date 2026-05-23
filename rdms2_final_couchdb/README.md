# Otopark Yönetim Sistemi

Bu proje, FastAPI ve CouchDB kullanılarak geliştirilmiş bir otopark yönetim sistemidir. Sistem, otopark alanlarını, araçları, kullanıcıları (sadece admin) ve giriş/çıkış işlemlerini yönetmek için modern bir web arayüzü ve RESTful API sunar.

## Özellikler
- Otopark alanı ekleme, silme, listeleme (sadece admin)
- Araç ekleme, silme, listeleme
- Araçların otoparklara atanması
- Giriş/çıkış işlemleri (kiosk)
- CouchDB bağlantı durumu arayüzde gösterilir
- Modern ve kullanıcı dostu web arayüzü (Bootstrap)
- Sadece bir admin kullanıcısı bulunur, kullanıcı yönetimi yoktur
- Sistem başlatıldığında veritabanı otomatik olarak sıfırlanır ve örnek veriler yüklenir

## Kurulum

1. **Gereksinimler:**
   - Python 3.8 veya üzeri
   - CouchDB (kurulu ve çalışır durumda olmalı)

2. **Projeyi klonlayın veya indirin:**
   
   ```bash
   git clone <proje-linki>
   cd rdms2_final
   ```

3. **Sanal ortam oluşturun ve aktif edin:**
   
   ```bash
   python -m venv .venv
   # Windows için:
   .venv\Scripts\activate
   # Linux/Mac için:
   source .venv/bin/activate
   ```

4. **Bağımlılıkları yükleyin:**
   
   ```bash
   pip install -r requirements.txt
   ```

5. **.env dosyasını düzenleyin:**
   
   CouchDB bağlantı bilgilerinizi `.env` dosyasına girin. Örnek:
   
   ```env
   COUCHDB_URL=http://admin:1234@localhost:5984/
   COUCHDB_USER=admin
   COUCHDB_PASSWORD=1234
   COUCHDB_DB=parking_lot
   PORT=5000
   ```

6. **Uygulamayı başlatın:**
   
   ```bash
   uvicorn app.main:app --reload --port 5000
   ```

7. **Web arayüzüne erişin:**
   
   Tarayıcınızda `http://localhost:5000` adresine gidin.

## Kullanım

- **Admin Girişi:**
  - Varsayılan admin kullanıcı adı: `admin`
  - Varsayılan şifre: `admin123`
  - Otopark ekleme ve silme işlemleri sadece admin tarafından yapılabilir.
- **Kiosk (Kullanıcı) Modu:**
  - Araç ekleme, giriş/çıkış işlemleri yapılabilir.
- **CouchDB Durumu:**
  - Web arayüzünün üst kısmında bağlantı durumu gösterilir.

## Notlar
- Sistem başlatıldığında tüm veritabanı sıfırlanır ve örnek veriler yüklenir.
- Proje, eğitim ve ödev amaçlı hazırlanmıştır.
- Geliştirme ve test için önerilen tarayıcı: Google Chrome veya Mozilla Firefox.

## Klasör Yapısı

```
rdms2_final/
│   .env
│   .gitignore
│   requirements.txt
│   README.md
└───app/
    │   main.py
    ├───models/
    ├───routes/
    ├───db/
    └───static/
```

## Lisans
Bu proje, yalnızca eğitim ve ödev amaçlıdır. Herhangi bir ticari kullanım için uygun değildir.
