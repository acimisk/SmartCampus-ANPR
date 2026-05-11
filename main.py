import sys
import re
import base64
import datetime
import collections
from ultralytics import YOLO
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
from dotenv import load_dotenv
import easyocr
import time

from gui.arayuz import Arayuz
from database.db_manager import DBManager

load_dotenv()

class ANPRWorker(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    plate_detected_signal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        # Son tespit edilen her plaka adayı için crop görselini saklar
        self.plate_images: dict[str, str] = {}  # plaka_metni -> base64 JPEG

    def run(self):
        import gc
        model = YOLO('campus_best.pt') 
        reader = easyocr.Reader(['tr', 'en'], gpu=True)
        cap = cv2.VideoCapture("kampus_test_videosu.mp4")

        recent_candidates = collections.deque(maxlen=20)
        last_logged_plate = ""
        last_log_time = 0
        frame_counter = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            frame_counter += 1

            if frame_counter % 2 == 0:
                results = model(frame, stream=True, conf=0.5, verbose=False) 
                
                for r in results:
                    for box in r.boxes:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        if (x2 - x1) < 100: continue
                        
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                        plate_crop = frame[y1:y2, x1:x2]

                        if plate_crop.size > 0:
                            ocr_result = reader.readtext(plate_crop)
                            full_text = "".join([re.sub(r'[^A-Z0-9]', '', t[1].upper()) for t in ocr_result])
                            if 7 <= len(full_text) <= 9:
                                recent_candidates.append(full_text)
                                # Crop görselini base64 olarak sakla
                                ok, jpeg = cv2.imencode('.jpg', plate_crop, [cv2.IMWRITE_JPEG_QUALITY, 90])
                                if ok:
                                    self.plate_images[full_text] = base64.b64encode(jpeg.tobytes()).decode('utf-8')
                                # Bellek: en fazla 15 farklı aday sakla
                                if len(self.plate_images) > 15:
                                    oldest = next(iter(self.plate_images))
                                    self.plate_images.pop(oldest)

            # Oylama ve Sinyal
            if len(recent_candidates) >= 15:
                most_common_plate, count = collections.Counter(recent_candidates).most_common(1)[0]
                if count >= 6 and most_common_plate != last_logged_plate:
                    if time.time() - last_log_time > 8: 
                        last_logged_plate = most_common_plate
                        last_log_time = time.time()
                        tarih = datetime.datetime.now().strftime("%H:%M:%S")
                        self.plate_detected_signal.emit(most_common_plate, tarih)
                        recent_candidates.clear()

            # GÖRÜNTÜ AKTARIMI (Hızlandırılmış)
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            
            # Sadece görüntü aktarırken copy yapıyoruz, her şeyi silmiyoruz
            qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888).copy()
            self.change_pixmap_signal.emit(qt_img)
            
            # Bellek temizliğini 100 karede bir yap (Hız için kritik!)
            if frame_counter % 100 == 0:
                gc.collect()
            
            self.msleep(1) # Gecikmeyi minimuma indirdik

        cap.release()

class SmartCampusApp(Arayuz):
    def __init__(self):
        super().__init__()
        
        # Veritabanı yöneticisini başlat
        self.db = DBManager()
        
        # Açılışta eski kayıtları yükle
        self.eski_verileri_yukle()
        
        # Arayüz ayarları
        self.video_label.setScaledContents(False)
        self.video_label.setAlignment(Qt.AlignCenter) 
        self.search_button.hide() 
        self.search_input.textChanged.connect(self.filter_table) 
        
        # İşçi başlat
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
        """DB'den gelen verileri tabloya dizer"""
        veriler = self.db.son_kayitlari_getir()
        for plaka, durum, tarih in veriler:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(plaka))
            self.table.setItem(row, 1, QTableWidgetItem(durum))
            self.table.setItem(row, 2, QTableWidgetItem(tarih))

    def update_table(self, plaka, tarih):
        # 1. AYNI PLAKAYI ÜST ÜSTE YAZMA (Lokal Filtre)
        if self.table.rowCount() > 0:
            last_added = self.table.item(0, 0).text()
            if last_added == plaka:
                return

        # 2. VERİTABANINA KAYDET (görsel de dahil)
        durum = self.db.erisim_durumu_getir(plaka) if self.db.collection is not None else "UNAUTHORIZED"
        gorsel = self.worker.plate_images.get(plaka)
        self.db.kaydet(plaka, tarih, durum, plaka_gorseli=gorsel)
        
        # 3. ARAYÜZE EKLE
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(plaka))
        self.table.setItem(0, 1, QTableWidgetItem(durum))
        self.table.setItem(0, 2, QTableWidgetItem(tarih))
        
        # Arama filtresi kontrolü
        search_text = self.search_input.text().upper().strip()
        if search_text and search_text not in plaka.upper():
            self.table.setRowHidden(0, True)

    def update_image(self, qt_img):
        if qt_img is None or qt_img.isNull():
            return

        try:
            # Görüntüyü derin kopyala (Deep Copy)
            temp_img = qt_img.copy() 
            
            # Boyut kontrolü
            label_size = self.video_label.size()
            if label_size.width() <= 0 or label_size.height() <= 0:
                return

            pixmap = QPixmap.fromImage(temp_img)
            
            # Ölçeklendirmeyi ana thread'i yormadan yap
            scaled = pixmap.scaled(
                label_size, 
                Qt.KeepAspectRatio, 
                Qt.FastTransformation
            )
            
            self.video_label.setPixmap(scaled)
            
            # Geçici nesneleri manuel silerek belleği rahatlat
            del temp_img
            del pixmap
        except Exception as e:
            print(f"🔥 Kritik Çizim Hatası: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartCampusApp()
    window.show()
    sys.exit(app.exec_())   