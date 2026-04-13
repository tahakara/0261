# Havayolu Yönetim Sistemi Veritabanı

Bu proje, havayolu firması için tam normalleştirilmiş (3NF) bir veritabanı şeması içerir.

## Klasör Yapısı

- **Database/** - PostgreSQL versiyonu
- **Database_MySQL/** - MySQL versiyonu

## Veritabanı Tabloları

### 1. **aircraft** - Uçak Filosu
- Uçak kod numarası, marka, model
- Yolcu kapasitesi, menzil bilgisi
- Aktif/bakım durumu

### 2. **passengers** - Yolcular
- Benzersiz yolcu numarası
- Ad, soyad bilgileri

### 3. **passenger_phones** - Yolcu Telefon Bilgileri
- Ev, cep, iş telefonu desteği
- Birincil telefon işaretleme
- Her yolcu için birden fazla telefon

### 4. **passenger_addresses** - Yolcu Adres Bilgileri
- Ev, iş, fatura, diğer adres tipleri
- Şehir, ülke, posta kodu
- Birincil adres işaretleme

### 5. **flights** - Uçuşlar
- Uçuş numarası, kalkış/varış noktaları
- Tarih, saat, uçak ataması
- Uçuş durumu

### 6. **flight_bookings** - Rezervasyonlar
- Yolcu-uçuş ilişkisi (Many-to-Many)
- Koltuk numarası
- Rezervasyon durumu

## PostgreSQL vs MySQL Farkları

### PostgreSQL (Database/)
- UUID veri tipi ile birincil anahtarlar
- `gen_random_uuid()` fonksiyonu
- `TIMESTAMP` veri tipi
- `BOOLEAN` veri tipi
- Daha gelişmiş trigger yapısı
- `COMMENT ON` syntax

### MySQL (Database_MySQL/)
- `CHAR(36)` ile UUID saklanır
- `UUID()` fonksiyonu
- `DATETIME` veri tipi
- `TINYINT(1)` ile boolean değerler
- `ON UPDATE CURRENT_TIMESTAMP` otomatik güncelleme
- Column-level comment syntax
- `CONCAT()` string birleştirme
- `CURDATE()` ve `DATE_ADD()` tarih fonksiyonları

## Kurulum

### PostgreSQL İçin
```bash
psql -U your_username -d your_database
\i Database/airline_database_schema.sql
\i Database/airline_sample_data.sql
```

### MySQL İçin
```bash
mysql -u your_username -p your_database
source Database_MySQL/airline_database_schema.sql
source Database_MySQL/airline_sample_data.sql
```

## Örnek Sorgular

Her iki klasörde de `airline_queries.sql` dosyası bulunur ve şu sorguları içerir:

1. Aktif uçakları listele
2. Belirli bir uçağın tüm uçuşları
3. Yolcunun uçuş geçmişi
4. Uçuştaki yolcu listesi
5. Uçak kullanım raporu
6. Müsait kapasiteli uçuşlar
7. Yolcu uçuş istatistikleri
8. Günlük uçuş programı
9. Bakımdaki uçaklar
10. Popüler rotalar
11. Birlikte uçan yolcular
12. Yaklaşan uçuşlar (7 gün)
13. Fazla rezervasyon kontrolü
14. Yolcu iletişim bilgileri
15. Uçak tipine göre uçuşlar
16. Tüm telefon dizini
17. Birincil telefon listesi
18. Yolcu başına telefon sayısı
19. Tüm adres dizini
20. Birincil adres listesi
21. Yolcu başına adres sayısı
22. Tam yolcu profili

## Veri Normalleşmesi

✅ **3. Normal Form (3NF)**
- Telefon ve adres bilgileri ayrı tablolarda
- Tekrarlayan veriler ortadan kaldırıldı
- Her veri tek bir yerde saklanır

✅ **Veri Bütünlüğü**
- Foreign key constraints
- CHECK constraints
- UNIQUE constraints
- CASCADE delete kuralları

✅ **Performans**
- Tüm önemli kolonlarda indexler
- Optimized JOIN operations

## Gereksinimler Uyumu

✅ Uçak bilgileri ve durumları  
✅ Uçuş detayları ve uçak ataması  
✅ Yolcu bilgileri ve numaralandırma  
✅ Yolcu-uçuş ilişkileri  
✅ Çoklu telefon ve adres desteği  
✅ Birincil telefon/adres işaretleme  

## Lisans

Eğitim amaçlı proje.
