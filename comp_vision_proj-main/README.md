# Image/Video Editor

Modern bir resim ve video düzenleyici uygulaması. PySide6 (Qt6) ve OpenCV kullanılarak geliştirilmiştir.

## Özellikler

- **Resim Düzenleme**: Resimler üzerinde efektler, filtreler ve düzenlemeler
- **Video Düzenleme**: Videolar üzerinde kare kare efekt uygulama
- **Layer Sistemi**: Photoshop benzeri çoklu katman desteği
- **Modüler Mimari**: Kolayca yeni efekt ve araçlar eklenebilir

## Kurulum

### Gereksinimler

- Python 3.10 veya üzeri
- pip (Python paket yöneticisi)

### Bağımlılıkları Yükleme

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python main.py
```

## Kullanım

### Uygulama Başlatıldığında

1. Açılış ekranında "Image Editor" veya "Video Editor" modunu seçin
2. Ana düzenleme arayüzü açılacaktır

### Arayüz Yapısı

```
┌─────────────────────────────────────────────────────────────┐
│                      Top Toolbar                            │
│  [Mode] [File ▼] [Edit ▼] | View: [-] [100%] [+] [⊞] [1:1] │
├──────────┬──────────────────────────────────┬───────────────┤
│          │                                  │ Module        │
│ Modules  │                                  │ Settings      │
│          │                                  │               │
│ ▼ Tools  │                                  ├───────────────┤
│   Brush  │         Canvas Area              │               │
│   Eraser │                                  │ Layers        │
│          │                                  │               │
│ ▼ Adjust │                                  │ [Layer 1]     │
│   Bright │                                  │ [Background]  │
│   Contr  │                                  │               │
│          │                                  │ [+][-][📋][↑][↓]│
├──────────┴──────────────────────────────────┴───────────────┤
│ Mode: Image | Cursor: 0,0 | Selection: None | 800×600 | 100%│
└─────────────────────────────────────────────────────────────┘
```

### Klavye Kısayolları

| Kısayol | İşlev |
|---------|-------|
| `Ctrl+N` | Yeni proje |
| `Ctrl+O` | Dosya aç |
| `Ctrl+S` | Kaydet |
| `Ctrl+Shift+S` | Farklı kaydet |
| `Ctrl+Z` | Geri al |
| `Ctrl+Y` | İleri al |
| `Ctrl++` | Yakınlaştır |
| `Ctrl+-` | Uzaklaştır |
| `Ctrl+0` | %100 boyut |
| `Ctrl+1` | Görünüme sığdır |
| `Escape` | Seçimi iptal et |

## Modül Ekleme

Yeni modüller eklemek için `src/modules/` dizinine yeni Python dosyaları ekleyin. Her modül `ModuleBase` sınıfından türetilmelidir.

### Örnek Modül

```python
from src.core.module_base import ModuleBase, ModuleCategory
import numpy as np
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider

class MyCustomModule(ModuleBase):
    @property
    def name(self) -> str:
        return "My Custom Effect"
    
    @property
    def description(self) -> str:
        return "Description of what this module does"
    
    @property
    def category(self) -> ModuleCategory:
        return ModuleCategory.EFFECT
    
    @property
    def supports_image(self) -> bool:
        return True
    
    @property
    def supports_video(self) -> bool:
        return True
    
    def get_settings_widget(self) -> QWidget:
        widget = QWidget()
        # Add your controls here
        return widget
    
    def apply(self, image: np.ndarray, **params) -> np.ndarray:
        # Apply your effect to the image
        return image
```

### Modül Kategorileri

- `TOOL`: Seçim, fırça, silgi vb. araçlar
- `ADJUSTMENT`: Parlaklık, kontrast vb. ayarlar
- `FILTER`: Bulanıklık, keskinlik vb. filtreler
- `EFFECT`: Artistik efektler
- `TRANSFORM`: Döndürme, ölçekleme, kırpma
- `COLOR`: Renk düzeltme ve grading
- `VIDEO`: Video özel araçlar
- `OTHER`: Diğer

## Proje Yapısı

```
.
├── main.py                 # Uygulama giriş noktası
├── requirements.txt        # Python bağımlılıkları
├── README.md              # Bu dosya
└── src/
    ├── __init__.py
    ├── core/              # Çekirdek sınıflar
    │   ├── module_base.py # Modül temel sınıfı
    │   ├── layer.py       # Layer sistemi
    │   └── project.py     # Proje yönetimi
    ├── ui/                # Kullanıcı arayüzü
    │   ├── main_window.py # Ana pencere
    │   ├── mode_selector.py # Mod seçim dialogu
    │   ├── canvas.py      # Canvas widget
    │   ├── sidebar_left.py # Sol panel (modüller)
    │   ├── sidebar_right.py # Sağ panel (ayarlar + layers)
    │   ├── toolbar.py     # Üst araç çubuğu
    │   └── statusbar.py   # Alt durum çubuğu
    ├── modules/           # Efekt ve araç modülleri
    │   ├── module_loader.py # Modül yükleyici
    │   └── examples.py    # Örnek modüller
    └── utils/             # Yardımcı fonksiyonlar
        ├── image_utils.py # Resim işlemleri
        └── video_utils.py # Video işlemleri
```

## Lisans

Bu proje MIT lisansı altında dağıtılmaktadır.
