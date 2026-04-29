from pymongo import MongoClient
import datetime
import os
import math
from dotenv import load_dotenv

load_dotenv()

class DBManager:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI")
        self.collection = None
        self.authorized_collection = None
        self.blacklist_collection = None

        if not self.uri:
            print("HATA: .env dosyasinda MONGODB_URI bulunamadi!")
            return

        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client["SmartCampus"]
            self.collection = self.db["plate_logs"]
            self.authorized_collection = self.db["authorized_plates"]
            self.blacklist_collection = self.db["blacklist_plates"]
            self.collection.create_index([("plaka_no", 1), ("kayit_tarihi", -1)])
            self.authorized_collection.create_index("plaka_no", unique=True)
            self.blacklist_collection.create_index("plaka_no", unique=True)
            print("MongoDB Atlas bulut baglantisi basariyla saglandi.")
        except Exception as e:
            self.collection = None
            self.authorized_collection = None
            self.blacklist_collection = None
            print(f"Baglanti hatasi: {e}")

    @staticmethod
    def _normalize_plate(plaka):
        return "".join(ch for ch in str(plaka).upper() if ch.isalnum())

    def erisim_durumu_getir(self, plaka):
        normalized = self._normalize_plate(plaka)
        if not normalized:
            return "UNAUTHORIZED"
        if self.blacklist_collection is None or self.authorized_collection is None:
            return "UNAUTHORIZED"

        try:
            if self.blacklist_collection.find_one({"plaka_no": normalized, "aktif": {"$ne": False}}):
                return "UNAUTHORIZED"
            if self.authorized_collection.find_one({"plaka_no": normalized, "aktif": True}):
                return "AUTHORIZED"
            return "UNAUTHORIZED"
        except Exception as e:
            print(f"Erisim durumu sorgulanamadi: {e}")
            return "UNAUTHORIZED"

    def sahip_bilgisi_getir(self, plaka):
        normalized = self._normalize_plate(plaka)
        if not normalized or self.authorized_collection is None:
            return None
        try:
            doc = self.authorized_collection.find_one({"plaka_no": normalized, "aktif": True})
            if not doc:
                return None
            return {
                "plaka_no": doc.get("plaka_no", ""),
                "sahip_adi": doc.get("sahip_adi", ""),
                "tip": doc.get("tip", "AUTHORIZED"),
            }
        except Exception as e:
            print(f"Sahip bilgisi sorgulanamadi: {e}")
            return None

    def plaka_listesine_ekle(self, plaka, liste_tipi, sahip_adi=""):
        normalized = self._normalize_plate(plaka)
        if not normalized:
            return False

        collection = self.authorized_collection if liste_tipi == "authorized" else self.blacklist_collection
        if collection is None:
            return False

        try:
            base_payload = {
                "plaka_no": normalized,
                "aktif": True,
                "guncelleme_tarihi": datetime.datetime.now(),
            }
            if liste_tipi == "authorized":
                base_payload["sahip_adi"] = sahip_adi.strip()
            collection.update_one(
                {"plaka_no": normalized},
                {"$set": base_payload},
                upsert=True,
            )
            return True
        except Exception as e:
            print(f"Plaka listesine eklenemedi: {e}")
            return False

    def plaka_listesinden_cikar(self, plaka, liste_tipi):
        normalized = self._normalize_plate(plaka)
        if not normalized:
            return False

        collection = self.authorized_collection if liste_tipi == "authorized" else self.blacklist_collection
        if collection is None:
            return False

        try:
            collection.update_one(
                {"plaka_no": normalized},
                {"$set": {"aktif": False, "guncelleme_tarihi": datetime.datetime.now()}},
                upsert=False,
            )
            return True
        except Exception as e:
            print(f"Plaka listeden cikarilamadi: {e}")
            return False

    def kaydet(self, plaka, tarih, durum="UNAUTHORIZED"):
        """Bulut veritabanına yeni plaka kaydeder"""
        if self.collection is None:
            return False

        try:
            normalized = self._normalize_plate(plaka)
            veri = {
                "plaka_no": normalized,
                "tarih_saat": tarih,
                "erisim_durumu": durum,
                "kayit_tarihi": datetime.datetime.now()
            }
            self.collection.insert_one(veri)
            return True
        except Exception as e:
            print(f"Veri kaydedilirken hata olustu: {e}")
            return False

    def son_kayitlari_getir(self, limit=20):
        """Buluttan son kayıtları çeker (Ekipteki herkes aynı veriyi görür)"""
        if self.collection is None:
            return []

        try:
            cursor = self.collection.find().sort("_id", -1).limit(limit)
            rows = []
            for doc in cursor:
                rows.append(
                    (
                        doc.get("plaka_no", ""),
                        doc.get("erisim_durumu", "UNAUTHORIZED"),
                        doc.get("tarih_saat", ""),
                    )
                )
            return rows
        except Exception as e:
            print(f"Veri cekilirken hata olustu: {e}")
            return []

    def loglardan_yetkili_oranini_ayarla(self, oran=0.9):
        if self.collection is None or self.authorized_collection is None:
            return 0, 0
        try:
            pipeline = [
                {"$group": {"_id": "$plaka_no", "adet": {"$sum": 1}}},
                {"$sort": {"adet": -1}},
            ]
            grouped = list(self.collection.aggregate(pipeline))
            if not grouped:
                return 0, 0

            toplam = len(grouped)
            yetkili_adet = max(1, math.ceil(toplam * oran))
            now = datetime.datetime.now()

            authorized_set = set()
            for idx, doc in enumerate(grouped):
                plate = self._normalize_plate(doc.get("_id", ""))
                if not plate:
                    continue
                is_authorized = idx < yetkili_adet
                if is_authorized:
                    authorized_set.add(plate)
                    self.authorized_collection.update_one(
                        {"plaka_no": plate},
                        {
                            "$set": {
                                "plaka_no": plate,
                                "aktif": True,
                                "sahip_adi": f"Kampus Kullanici {idx + 1}",
                                "guncelleme_tarihi": now,
                            }
                        },
                        upsert=True,
                    )
                else:
                    self.authorized_collection.update_one(
                        {"plaka_no": plate},
                        {"$set": {"aktif": False, "guncelleme_tarihi": now}},
                        upsert=True,
                    )
            return toplam, len(authorized_set)
        except Exception as e:
            print(f"90% yetki dagitimi basarisiz: {e}")
            return 0, 0