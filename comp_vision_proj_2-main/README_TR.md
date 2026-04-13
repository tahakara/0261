# Vision Editor
### Eklenti Tabanlı Modüler Görüntü ve Video İşleme Yazılımı

Python, PySide6 ve OpenCV ile geliştirilmiş profesyonel düzeyde görüntü ve video editörü. Genişletilebilirlik için güçlü eklenti mimarisi içerir. UI/UX Adobe Photoshop ve Premiere'den esinlenilmiştir.

---

## 🚀 Özellikler

### Temel Mimari
- **Eklenti Tabanlı Sistem**: Araçları, efektleri, filtreleri ve ayarlamaları dinamik olarak yükleyin ve yönetin
- **İkili Mod**: Görüntü Editörü ve Video Editörü modları arasında geçiş yapın
- **Profesyonel Arayüz**: Endüstri standardı araçlardan esinlenen sezgisel düzen ile koyu tema
- **Yüksek Performans**: QGraphicsView ve OpenCV ile optimize edilmiş render

### Görüntü Editörü Modu
#### Kullanıcı Arayüzü
- **Üst Çubuk**: Menü çubuğu (Dosya, Düzenle, Görünüm, Eklentiler, Yardım) ve hızlı eylemler için araç çubuğu
- **Sol Kenar Çubuğu (Araç Kutusu)**: Yüklü eklentilerle dinamik olarak doldurulur
- **Sağ Kenar Çubuğu**: 
  - **Araç Ayarları Paneli** (Üst): Aktif eklentiye göre değişen dinamik ayarlar
  - **Katman Yönetimi Paneli** (Alt): Tam kontroller ile gelişmiş katman sistemi
- **Merkez Kanvas**: Yakınlaştırma/kaydırma ile yüksek performanslı QGraphicsView tabanlı çalışma alanı

#### Katman Sistemi
- Küçük resimlerle çoklu katman desteği
- Katman görünürlük değiştirme
- Opaklık kontrolü (0-100%)
- Karışım modları: Normal, Çarpma, Ekran, Üst Üste Bindirme, Ekleme, Çıkarma
- Katman sıralama (yukarı/aşağı taşı)
- Katman kilitleme
- Gerçek zamanlı birleştirme

#### Eklenti Türleri
1. **Araç Eklentileri**: Etkileşimli araçlar (örn. Fırça, Seçim, Şekiller)
2. **Efekt Eklentileri**: Görüntü efektleri (örn. Bulanıklık, Keskinleştirme)
3. **Filtre Eklentileri**: Renk ve stil filtreleri
4. **Ayarlama Eklentileri**: Görüntü ayarlamaları (örn. Parlaklık, Kontrast)

#### Şekil Çizim Aracı
- **Şekiller**: Dikdörtgen, Daire, Çizgi, Ok, Elips, Üçgen
- **Özelleştirme**: Renk seçimi, kalınlık kontrolü, dolu/çizgili seçenekler
- **Gerçek Zamanlı Önizleme**: Şekilleri çizerken görün

### Video Editörü Modu
#### Kamera ve Kayıt
- **Canlı Kamera Görüntüsü**: Ayarlanabilir FPS ile gerçek zamanlı kamera yakalama
- **Kayıt**: 
  - Çoklu format desteği (MP4, AVI, MOV, MKV)
  - Codec seçimi (H.264, MJPEG, X264)
  - Kayıt sırasında süre zamanlayıcı gösterimi
  - REC göstergesi yer paylaşımı
- **Snapshot**: Canlı görüntüden sabit kareler yakalayın

#### Video Efektleri
- **Temel Ayarlamalar**:
  - Parlaklık kontrolü (-100 ile +100)
  - Isı/Sıcaklık efekti (0-100%)
  - Gürültü azaltma gücü (0-10)
  - Gürültü ekleme (0-100%)
  
- **RGB Kanal Kontrolü**:
  - Bağımsız Kırmızı, Yeşil, Mavi kanal ayarlamaları (-100 ile +100)
  - Gerçek zamanlı renk düzeltme

#### Yüz Algılama ve Analiz
- **Yüz Algılama** (Haar Cascade):
  - Otomatik yüz algılama
  - Numaralandırma ile sınırlayıcı kutular
  - Ayarlanabilir bulanıklık gücü (1-49, sadece tek sayılar)
  - Yüze özel bulanıklık efekti
  
- **Duygu Analizi**:
  - Gerçek zamanlı duygu tespiti (Mutlu, Üzgün, Nötr)
  - Karede görsel emoji göstergeleri
  - Emoji gösterimini değiştirme
  - Doğru tespit için uyarlanabilir eşikler

#### Renk Filtreleri
Ayarlanabilir yoğunlukla dokuz sanatsal filtre (0-100%):
1. **Sepya**: Klasik sıcak vintage ton
2. **Gri Tonlama**: Siyah beyaz dönüşüm
3. **Negatif**: Ters çevrilmiş renkler
4. **Vintage**: Eskimiş fotoğraf efekti
5. **Soğuk Ton**: Mavi tonlu soğuk efekt
6. **Sıcak Ton**: Turuncu tonlu sıcak efekt
7. **Yüksek Kontrast**: CLAHE uyarlanabilir kontrast
8. **Canlı**: Artırılmış doygunluk
9. **Siyah ve Beyaz**: İkili eşik efekti

#### Video Overlay Sistemi
- **Metin Overlay'leri**:
  - 7 OpenCV yazı tipi ailesi (HERSHEY_SIMPLEX, DUPLEX, COMPLEX, vb.)
  - Özel metin, boyut, renk, konum
  - Opaklık kontrolü (0-100%)
  - Varsayılan isimlendirme ile isimlendirilmiş overlay'ler
  
- **Görüntü Overlay'leri**:
  - Alfa kanallı PNG/JPG desteği
  - Konum ve boyut kontrolü
  - Chroma key (yeşil ekran) desteği
  - Ayarlanabilir keycolor toleransı
  
- **Video Overlay'leri**:
  - Overlay olarak video oynatma
  - Döngülü oynatma
  - Konum ve boyut kontrolü
  - Chroma key desteği
  
- **Overlay Yönetimi**:
  - Overlay'leri isimlendirme ve yeniden isimlendirme
  - Görsel çerçeve ve yeniden boyutlandırma tutamakları ile seçim
  - Seçmek için tıklayın, seçimi kaldırmak için dışarıya tıklayın
  - Gerçek zamanlı güncellemeler
  - Overlay isimleriyle liste görünümü

---

## 📦 Kurulum

### Gereksinimler
- Python 3.9 veya üzeri
- pip paket yöneticisi

### Kurulum Adımları

1. **Projeyi klonlayın veya indirin**
```bash
cd comp_vision_proj
```

2. **Bağımlılıkları yükleyin**
```bash
pip install -r requirements.txt
```

---

## 🎯 Kullanım

### Uygulamayı Çalıştırma

```bash
python main.py
```

### İş Akışı

#### Görüntü Editörü Modu
1. **Başlatma Ekranı**: "Görüntü Editörü" modunu seçin
2. **Ana Editör**: 
   - Yeni proje oluşturun veya mevcut görüntüyü açın
   - Sol kenar çubuğundan araçları seçin
   - Sağ üst panelde araç ayarlarını yapın
   - Sağ alt panelde katmanları yönetin
   - Kanvas kontrollerini kullanın: yakınlaştırma, kaydırma, pencereye sığdır
   - Özelleştirilebilir renk ve stillerle şekiller çizin

#### Video Editörü Modu
1. **Başlatma Ekranı**: "Video Editörü" modunu seçin
2. **Kamera Kurulumu**:
   - Kamera görüntüsünü başlatmak için "Kamerayı Aç"a tıklayın
   - Video efektlerini gerçek zamanlı olarak ayarlayın
   
3. **Yüz Algılama ve Analiz**:
   - Yüz algılama için "Yüz Tanıma Aktif"i etkinleştirin
   - Sınırlayıcı kutuları, numaralandırmayı, bulanıklığı değiştirin
   - Duygu tespiti için "Duygu Analizi"ni etkinleştirin
   - Gizlilik için bulanıklık gücünü ayarlayın
   
4. **Efekt Uygulama**:
   - Parlaklık, ısı, gürültü azaltma, gürültü ayarlayın
   - RGB kanallarını ayrı ayrı değiştirin
   - Yoğunluk kontrolü ile renk filtreleri seçin
   
5. **Overlay Ekleme**:
   - Metin: Metin girin, yazı tipi, renk, boyut seçin
   - Görüntü: PNG/JPG dosyalarına göz atın ve yükleyin
   - Video: Chroma key ile video overlay'leri ekleyin
   - Düzenleme için overlay'leri isimlendirin
   - Seçmek ve yeniden boyutlandırmak için overlay'lere tıklayın
   
6. **Kayıt**:
   - Video formatı seçin (MP4, AVI, MOV, MKV)
   - Kayda başlamak için "Kaydı Başlat"a tıklayın
   - Süre zamanlayıcısını izleyin
   - Durdurmak ve kaydetmek için "Kaydı Durdur"a tıklayın
   
7. **Snapshot**:
   - Mevcut kareyi yakalamak için "Snapshot Al"a tıklayın
   - PNG/JPG olarak kaydedin

### Klavye Kısayolları

| Kısayol | Eylem |
|---------|-------|
| `Ctrl+N` | Yeni Proje |
| `Ctrl+O` | Dosya Aç |
| `Ctrl+S` | Kaydet |
| `Ctrl+Shift+S` | Farklı Kaydet |
| `Ctrl++` | Yakınlaştır |
| `Ctrl+-` | Uzaklaştır |
| `Ctrl+0` | Pencereye Sığdır |
| `Ctrl+R` | Görünümü Sıfırla |
| `Ctrl+Q` | Çıkış |

---

## 🔌 Eklenti Geliştirme

### Yeni Eklenti Oluşturma

Eklentiler, `plugins/` dizinine yerleştirilen basit Python dosyalarıdır. Farklı eklenti türlerinin nasıl oluşturulacağı:

#### 1. Araç Eklentisi Örneği

```python
from src.plugin_base import ToolPlugin
import numpy as np

class MyTool(ToolPlugin):
    def __init__(self):
        super().__init__()
        self.name = "Aracım"
        self.description = "Aracımın açıklaması"
        
    def get_name(self):
        return self.name
    
    def get_icon(self):
        return ""
    
    def get_settings_widget(self):
        # Araç ayarlarıyla QWidget döndür
        return None
    
    def apply(self, image, layer_manager):
        # Araç mantığını uygula
        return image
```

#### 2. Efekt Eklentisi Örneği

```python
from src.plugin_base import EffectPlugin
import cv2

class MyEffect(EffectPlugin):
    def __init__(self):
        super().__init__()
        self.name = "Efektim"
        self.description = "Efektimin açıklaması"
        
    def apply_effect(self, image):
        # Efekt mantığını uygula
        return cv2.GaussianBlur(image, (5, 5), 0)
```

### Eklenti Temel Sınıfları

- `ToolPlugin`: Etkileşimli araçlar için (fırça, seçim, vb.)
- `EffectPlugin`: Görüntü efektleri için (bulanıklık, keskinleştirme, vb.)
- `FilterPlugin`: Filtreler için (renk derecelendirme, vb.)
- `AdjustmentPlugin`: Ayarlamalar için (parlaklık, kontrast, vb.)

---

## 📁 Proje Yapısı

```
comp_vision_proj/
├── main.py                    # Uygulama giriş noktası
├── requirements.txt           # Bağımlılıklar
├── README.md                  # İngilizce dokümantasyon
├── README_TR.md               # Türkçe dokümantasyon (bu dosya)
├── .gitignore                 # Git ignore kuralları
│
├── src/                       # Kaynak kod
│   ├── __init__.py
│   ├── launcher_window.py     # Mod seçimi ile hoş geldiniz ekranı
│   ├── editor_window.py       # Ana editör penceresi (ikili mod)
│   ├── canvas.py              # Kanvas render sistemi
│   ├── layer_manager.py       # Katman yönetim sistemi
│   ├── plugin_base.py         # Eklenti temel sınıfları
│   ├── plugin_manager.py      # Eklenti yükleyici ve yönetici
│   │
│   # Video Editörü Bileşenleri
│   ├── video_system.py        # Kamera yakalama ve video işleme
│   ├── video_control_panel.py # Video efektleri ve kontroller UI
│   ├── overlay_manager.py     # Metin/görüntü/video overlay sistemi
│   ├── overlay_panel.py       # Overlay yönetim UI
│   ├── face_detection.py      # Haar Cascade yüz algılama
│   ├── face_sentiment.py      # Duygu analiz sistemi
│   ├── color_filters.py       # 9 sanatsal renk filtresi
│   │
│   # Görüntü Editörü Bileşenleri
│   └── shape_tool.py          # Geometrik şekil çizim aracı
│
├── plugins/                   # Eklenti dizini (dinamik yükleme)
│   ├── brush_tool.py          # Fırça aracı
│   ├── blur_effect.py         # Bulanıklık efekti
│   ├── brightness_adjustment.py  # Parlaklık ayarlama
│   └── sharpen_filter.py      # Keskinleştirme filtresi
│
├── output/                    # Kaydedilen videolar (gitignore)
├── snapshots/                 # Yakalanan görüntüler (gitignore)
└── assets/                    # Varlıklar (simgeler, görüntüler, vb.)
```

---

## 🛠️ Teknik Detaylar

### Kullanılan Teknolojiler
- **PySide6 6.6.1**: Python için modern Qt6 bağlantıları
- **OpenCV 4.8.1.78**: Bilgisayarla görme ve görüntü işleme
- **NumPy 1.26.2**: Sayısal hesaplama ve dizi işlemleri
- **Pillow 10.1.0**: Görüntü formatı desteği

### Ana Bileşenler

#### Video Sistemi
- Yapılandırılabilir FPS ile gerçek zamanlı kamera yakalama (varsayılan 25 fps)
- Çoklu format video kodlama (mp4v, MJPEG, X264, H264)
- Efekt hattı: Yüz algılama → Duygu → RGB → Parlaklık → Isı → Gürültü Azaltma → Gürültü → Filtreler → Overlay'ler
- Sinyal/slot mimarisi ile QTimer tabanlı kare işleme

#### Yüz Algılama Sistemi
- Haar Cascade sınıflandırıcı (haarcascade_frontalface_default.xml)
- Yapılandırılabilir parametreler: scale_factor=1.1, min_neighbors=5, min_size=(30,30)
- Tek kernel boyutları ile Gaussian bulanıklık (1-49)
- Sınırlayıcı kutular ve numaralandırma ile gerçek zamanlı yüz takibi

#### Duygu Analizi
- Sezgisel tabanlı duygu tespiti (Mutlu, Üzgün, Nötr)
- Ağız bölgesi varyansı ve parlaklığını analiz eder
- Dengeli tespit için uyarlanabilir eşikler
- Emoji göstergeleri ile görsel geri bildirim

#### Overlay Sistemi
- Benzersiz ID'lerle dataclass tabanlı overlay yönetimi
- Şeffaflık için BGRA alfa karıştırma
- Ayarlanabilir toleransla chroma key (yeşil ekran)
- Görsel çerçeveler ve yeniden boyutlandırma tutamakları ile seçim sistemi
- Döngülü oynatma ile gerçek zamanlı video overlay oynatma

#### Renk Filtresi Sistemi
- Filtre uygulaması için statik metodlar
- cv2.addWeighted() ile yoğunluk tabanlı karıştırma
- Uyarlanabilir histogram eşitleme için CLAHE
- HSV ve LAB renk alanı dönüşümleri

---

## 🤝 Katkıda Bulunma

1. Projeyi fork edin
2. Feature branch'i oluşturun (`git checkout -b feature/YeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`)
4. Branch'i push edin (`git push origin feature/YeniOzellik`)
5. Pull Request açın

---

## 📝 Lisans

Bu proje eğitim amaçlıdır.

---

## 📧 İletişim

Sorularınız veya önerileriniz için issue açabilirsiniz.

---

## 🙏 Teşekkürler

- OpenCV topluluğuna
- PySide6 ekibine
- Tüm katkıda bulunanlara
