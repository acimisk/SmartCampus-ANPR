import sys
import cv2
import re
import datetime
import collections
import time
import difflib # YENİ EKLENDİ: Benzerlik kontrolü için
import gc
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
from ultralytics import YOLO
import easyocr

from gui.arayuz import Arayuz
from database.db_manager import DBManager

class ANPRWorker(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    plate_detected_signal = pyqtSignal(str, str)

    def run(self):
        import gc
        model = YOLO('campus_best.pt') 
        reader = easyocr.Reader(['tr', 'en'], gpu=True)
        cap = cv2.VideoCapture("kampus_test_videosu.mp4")

        recent_candidates = collections.deque(maxlen=20)
        last_logged_plate = ""
        last_log_time = 0
        last_auth_status = "AUTHORIZED" 
        frame_counter = 0
        
        KILIT_SURESI = 6 
        
        # 🚨 KARA LİSTE (Blacklist) - İstenmeyen Plakalar Güncellendi
        unauthorized_plates = {"234BP86", "03BCJ91", "23IGC972", "06BCY359", "72ACY846", "23BJ503", "23AEL187"}

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame_counter += 1
            current_time = time.time()

            results = model(frame, stream=True, conf=0.5, verbose=False) 
            
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    if (x2 - x1) < 100: continue 
                    
                    # --- KİLİT AKTİF Mİ? (Karar Verilmiş Durum) ---
                    if current_time - last_log_time < KILIT_SURESI:
                        
                        # Yetki durumuna göre OpenCV renklerini ayarla (Mavi, Yeşil, Kırmızı - BGR formatı)
                        if last_auth_status == "UNAUTHORIZED":
                            renk = (0, 0, 255) # Kırmızı
                        else:
                            renk = (0, 255, 0) # Yeşil
                            
                        # Kutuyu Çiz
                        cv2.rectangle(frame, (x1, y1), (x2, y2), renk, 3)
                        
                        # Yazıyı ve Arka Planı Hazırla
                        yazi = f"{last_logged_plate} - {last_auth_status}"
                        (w_text, h_text), _ = cv2.getTextSize(yazi, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                        
                        # Dinamik Arka Plan Kutusu (Renge Göre)
                        cv2.rectangle(frame, (x1, y1 - 35), (x1 + w_text, y1), renk, -1)
                        # Siyah Yazı
                        cv2.putText(frame, yazi, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)
                    
                    # --- KİLİT YOK (Tarama / Okuma Modu) ---
                    else:
                        # İşlem yapıldığını belli etmek için MAVİ kutu çiziyoruz
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 3)
                        
                        if frame_counter % 2 == 0:
                            plate_crop = frame[y1:y2, x1:x2]

                            if plate_crop.size > 0:
                                ocr_result = reader.readtext(plate_crop)
                                full_text = "".join([re.sub(r'[^A-Z0-9]', '', t[1].upper()) for t in ocr_result])
                                
                                if 7 <= len(full_text) <= 9:
                                    recent_candidates.append(full_text)

            # --- OYLAMA VE YETKİ KONTROLÜ ---
            if current_time - last_log_time >= KILIT_SURESI:
                if len(recent_candidates) >= 12:
                    most_common_plate, count = collections.Counter(recent_candidates).most_common(1)[0]
                    
                    if count >= 4:
                        last_logged_plate = most_common_plate
                        last_log_time = current_time
                        
                        # 🚨 YENİ: Veritabanına/Loglara yazmadan önce yetkiyi kontrol et
                        if last_logged_plate in unauthorized_plates:
                            last_auth_status = "UNAUTHORIZED"
                        else:
                            last_auth_status = "AUTHORIZED"
                            
                        tarih = datetime.datetime.now().strftime("%H:%M:%S")
                        
                        # İster yetkili ister yetkisiz olsun kaydı veritabanına atıyoruz
                        # (Güvenlik kameraları ihlalleri de kaydeder)
                        self.plate_detected_signal.emit(most_common_plate, tarih)
                        recent_candidates.clear()

            # GÖRÜNTÜYÜ ARAYÜZE GÖNDER
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888).copy()
            
            self.change_pixmap_signal.emit(qt_img)
            
            if frame_counter % 100 == 0:
                gc.collect() 
            
            self.msleep(1)

        cap.release()

class SmartCampusApp(Arayuz):
    def __init__(self):
        super().__init__()
        self.db = DBManager()
        self.eski_verileri_yukle()
        
        self.video_label.setScaledContents(False)
        self.video_label.setAlignment(Qt.AlignCenter) 
        self.search_button.hide() 
        self.search_input.textChanged.connect(self.filter_table) 
        
        self.worker = ANPRWorker()
        self.worker.change_pixmap_signal.connect(self.update_image)
        self.worker.plate_detected_signal.connect(self.update_table)
        self.worker.start()

    def filter_table(self):
        search_text = self.search_input.text().upper().strip()
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item:
                self.table.setRowHidden(row, search_text not in item.text().upper())

    def eski_verileri_yukle(self):
        """Veritabanındaki eski kayıtları arayüze yükler (Data uyuşmazlığı korumalı)"""
        veriler = self.db.son_kayitlari_getir()
        
        # Eğer veritabanı boşsa veya bağlantı hatası olduysa işlemi pas geç
        if not veriler:
            return

        for kayit in veriler:
            # 1. DURUM: Eğer veri MongoDB'den direkt JSON/Sözlük olarak geliyorsa
            if isinstance(kayit, dict):
                plaka = kayit.get('plaka_no', 'Bilinmeyen Plaka')
                tarih = kayit.get('tarih_saat', 'Bilinmeyen Tarih')
            # 2. DURUM: Eğer veri bizim db_manager'da yazdığımız gibi (plaka, tarih) tuple'ı olarak geliyorsa
            else:
                try:
                    plaka, tarih = kayit[0], kayit[1]
                except ValueError:
                    continue # Hatalı formatı atla

            # Veriyi arayüzdeki tabloya ekle
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(plaka))
            self.table.setItem(row, 1, QTableWidgetItem(tarih))

    def update_table(self, plaka, tarih):
        # Arayüz tablosunda en son eklenen ile birebir aynıysa ekleme (Arayüz koruması)
        if self.table.rowCount() > 0:
            last_added = self.table.item(0, 0).text()
            if last_added == plaka:
                return

        # Buluta Kaydet
        self.db.kaydet(plaka, tarih)
        
        # Tabloya Ekle
        search_text = self.search_input.text().upper().strip()
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(plaka))
        self.table.setItem(0, 1, QTableWidgetItem(tarih))
        
        if search_text and search_text not in plaka.upper():
            self.table.setRowHidden(0, True)

    def update_image(self, qt_img):
        if qt_img is None or qt_img.isNull():
            return
        try:
            temp_img = qt_img.copy() 
            label_size = self.video_label.size()
            if label_size.width() <= 0 or label_size.height() <= 0:
                return

            pixmap = QPixmap.fromImage(temp_img)
            scaled = pixmap.scaled(label_size, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.video_label.setPixmap(scaled)
            
            del temp_img
            del pixmap
        except Exception as e:
            print(f"⚠️ Çizim Hatası: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartCampusApp()
    window.showMaximized()
    sys.exit(app.exec_())