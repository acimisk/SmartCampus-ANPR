# Smart Campus ANPR & Access Control System

Bu proje, kampüs giriş-çıkışlarındaki araç geçişlerini izlemek ve yönetmek amacıyla geliştirilmiş otomatik plaka tanıma (ANPR) sistemidir. Sistem, video akışı üzerinden araç plakalarını gerçek zamanlı olarak tespit eder, metne dönüştürür ve geçiş yapılan tam saniye bilgisiyle birlikte veritabanına kaydeder. 

Geliştirilen kullanıcı arayüzü sayesinde, sistemde kayıtlı bir plaka sorgulanabilir ve video otomatik olarak aracın geçtiği ilgili saniyeye senkronize edilebilir.

## Temel Özellikler
* Video akışı üzerinden özel eğitilmiş YOLO modeli ile dinamik araç ve plaka tespiti.
* EasyOCR kullanılarak plaka üzerindeki karakterlerin metne (String) dönüştürülmesi.
* Tespit edilen plakanın authorized/blacklist listeleriyle anlik karsilastirilmasi.
* Tespit edilen plakaların, erisim durumu ve zaman bilgisiyle birlikte loglanmasi.
* Modern PyQt5 dashboard ile canli video, son tespit bilgisi ve olay tablosu.

## Kullanılan Teknolojiler
* **Dil:** Python 3.x
* **Görüntü İşleme:** OpenCV
* **Nesne Tespiti:** YOLO (Ultralytics)
* **Karakter Tanıma:** EasyOCR
* **Veritabanı:** MongoDB Atlas
* **Arayüz:** PyQt5

## Ortam Degiskenleri
`.env` dosyasina su degiskenleri eklenmelidir:

- `MONGODB_URI`: MongoDB Atlas baglanti dizesi
- `YOLO_MODEL_PATH` (opsiyonel): YOLO model dosya yolu (varsayilan: `campus_best.pt`)
- `VIDEO_SOURCE` (opsiyonel): Video dosya yolu veya kamera indeksi (varsayilan: `kampus_test_videosu.mp4`)
- `DETECT_EVERY_N_FRAMES` (opsiyonel): YOLO calisma araligi (varsayilan: `1`)
- `OCR_EVERY_N_DETECTIONS` (opsiyonel): OCR calisma araligi (varsayilan: `1`)
- `MAX_DETECTION_WIDTH` (opsiyonel): Tespit icin maksimum genislik (varsayilan: `1280`)
- `DECISION_LOCK_SECONDS` (opsiyonel): Ayni plakanin tekrar loglanmasi icin bekleme suresi (varsayilan: `15`)

## Erişim Listesi Yönetimi
Yetkili ve kara liste plakalarini terminalden yonetmek icin:

- Ekleme:
`python -m database.manage_access_lists add authorized 34ABC123`
- Kara listeye ekleme:
`python -m database.manage_access_lists add blacklist 06XYZ789`
- Listeden pasif etme:
`python -m database.manage_access_lists remove authorized 34ABC123`
