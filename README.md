# Smart Campus ANPR & Access Control System

Bu proje, kampüs giriş-çıkışlarındaki araç geçişlerini izlemek ve yönetmek amacıyla geliştirilmiş otomatik plaka tanıma (ANPR) sistemidir. Sistem, video akışı üzerinden araç plakalarını gerçek zamanlı olarak tespit eder, metne dönüştürür ve geçiş yapılan tam saniye bilgisiyle birlikte veritabanına kaydeder. 

Geliştirilen kullanıcı arayüzü sayesinde, sistemde kayıtlı bir plaka sorgulanabilir ve video otomatik olarak aracın geçtiği ilgili saniyeye senkronize edilebilir.

## Temel Özellikler
* Video akışı üzerinden özel eğitilmiş YOLO modeli ile dinamik araç ve plaka tespiti.
* EasyOCR kullanılarak plaka üzerindeki karakterlerin metne (String) dönüştürülmesi.
* Tespit edilen plakaların, videodaki geçiş zamanıyla (timestamp) birlikte loglanması.
* PyQt5 tabanlı arayüz üzerinden veritabanı sorgulama ve video oynatıcı senkronizasyonu.

## Kullanılan Teknolojiler
* **Dil:** Python 3.x
* **Görüntü İşleme:** OpenCV
* **Nesne Tespiti:** YOLO (Ultralytics)
* **Karakter Tanıma:** EasyOCR
* **Veritabanı:** SQLite
* **Arayüz:** PyQt5
