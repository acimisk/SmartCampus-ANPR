from pymongo import MongoClient
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DBManager:
    def __init__(self):
        
        self.uri = os.getenv("MONGODB_URI")
        
        if not self.uri:
            print("❌ HATA: .env dosyasında MONGODB_URI bulunamadı!")
            return

        try:
            self.client = MongoClient(self.uri)
            self.db = self.client['SmartCampus']
            self.collection = self.db['plate_logs']
            print("✅ MongoDB Atlas Bulut Bağlantısı Güvenli Şekilde Sağlandı!")
        except Exception as e:
            print(f"❌ Bağlantı Hatası: {e}")

    def kaydet(self, plaka, tarih):
        """Bulut veritabanına yeni plaka kaydeder"""
        try:
            veri = {
                "plaka_no": plaka,
                "tarih_saat": tarih,
                "kayit_tarihi": datetime.datetime.now()
            }
            self.collection.insert_one(veri)
        except Exception as e:
            print(f"❌ Veri kaydedilirken hata oluştu: {e}")

    def son_kayitlari_getir(self, limit=20):
        """Buluttan son kayıtları çeker (Ekipteki herkes aynı veriyi görür)"""
        try:
            # En yeni kayıtları en üstte getirmek için _id'ye göre ters sıralıyoruz
            cursor = self.collection.find().sort("_id", -1).limit(limit)
            rows = []
            for doc in cursor:
                rows.append((doc['plaka_no'], doc['tarih_saat']))
            return rows
        except Exception as e:
            print(f"❌ Veri çekilirken hata oluştu: {e}")
            return []
# db_manager.py dosyasının en sonuna ekle:

if __name__ == "__main__":
    # Sınıftan bir nesne oluştur (İşte marşa basılan yer burası)
    db = DBManager()
    
    # Bir test verisi kaydetmeyi dene
    print("Test verisi kaydediliyor...")
    db.kaydet("23KN2323", "12:00:00")
    
    # Verileri çekmeyi dene
    veriler = db.son_kayitlari_getir(limit=5)
    print("Bulunan son kayıtlar:", veriler)