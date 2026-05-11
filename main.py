import sys
import cv2
import re
import datetime
import collections
import time
import difflib 
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
    plate_detected_signal = pyqtSignal(str, str, str)

    def run(self):
        import gc
        model = YOLO('campus_best.pt') 
        reader = easyocr.Reader(['tr', 'en'], gpu=True)
        cap = cv2.VideoCapture("kampus_test_videosu.mp4")

        recent_candidates = collections.deque(maxlen=20)
        last_logged_plate = ""
        last_log_time = 0
        last_auth_status = "AUTHORIZED" 
        last_box_coords = (0, 0, 0, 0) # Başlangıç değeri eklendi
        frame_counter = 0
        
        KILIT_SURESI = 6 
        
        # 🚨 KARA LİSTE (Blacklist)
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
                    
                    # --- KİLİT AKTİF Mİ? ---
                    if current_time - last_log_time < KILIT_SURESI:
                        if last_auth_status == "UNAUTHORIZED":
                            renk = (0, 0, 255) # Kırmızı
                        else:
                            renk = (0, 255, 0) # Yeşil
                            
                        cv2.rectangle(frame, (x1, y1), (x2, y2), renk, 3)
                        yazi = f"{last_logged_plate} - {last_auth_status}"
                        (w_text, h_text), _ = cv2.getTextSize(yazi, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
                        cv2.rectangle(frame, (x1, y1 - 35), (x1 + w_text, y1), renk, -1)
                        cv2.putText(frame, yazi, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2, cv2.LINE_AA)

                        # CANLI CROP GÖSTERİMİ
                        live_crop = frame[y1:y2, x1:x2]
                        if live_crop.size > 0:
                            c_h, c_w = live_crop.shape[:2]
                            target_h = 60
                            target_w = int(c_w * (target_h / c_h))
                            y_start, y_end = y1 - 45 - target_h, y1 - 45
                            x_end = x1 + target_w
                            if y_start > 0 and x_end < frame.shape[1]:
                                scaled_crop = cv2.resize(live_crop, (target_w, target_h))
                                frame[y_start:y_end, x1:x_end] = scaled_crop
                                cv2.rectangle(frame, (x1, y_start), (x_end, y_end), renk, 2)
                    
                    # --- KİLİT YOK (Tarama Modu) ---
                    else:
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
                        last_box_coords = (x1, y1, x2, y2)
                        last_logged_plate = most_common_plate
                        last_log_time = current_time
                        
                        if last_logged_plate in unauthorized_plates:
                            last_auth_status = "UNAUTHORIZED"
                        else:
                            last_auth_status = "AUTHORIZED"
                            
                        tarih = datetime.datetime.now().strftime("%H:%M:%S")
                        self.plate_detected_signal.emit(most_common_plate, last_auth_status, tarih)
                        recent_candidates.clear()
            
            # --- GHOSTING ÖNLEYİCİ ---
            elif last_log_time != 0:
                old_center_x = (last_box_coords[0] + last_box_coords[2]) / 2
                new_center_x = (x1 + x2) / 2
                if abs(new_center_x - old_center_x) > 150:
                    last_log_time = 0
                    last_auth_status = "SCANNING"

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888).copy()
            self.change_pixmap_signal.emit(qt_img)
            if frame_counter % 100 == 0: gc.collect() 
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
        veriler = self.db.son_kayitlari_getir()
        if not veriler: return
        for kayit in veriler:
            if isinstance(kayit, dict):
                plaka = kayit.get('plaka_no', 'Bilinmeyen Plaka')
                tarih = kayit.get('tarih_saat', 'Bilinmeyen Tarih')
            else:
                try: plaka, tarih = kayit[0], kayit[1]
                except ValueError: continue
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(plaka))
            self.table.setItem(row, 1, QTableWidgetItem(tarih))

    # --- HATA BURADAYDI: 'durum' parametresi eklendi ---
    def update_table(self, plaka, durum, tarih):
        if self.table.rowCount() > 0:
            last_added = self.table.item(0, 0).text()
            if last_added == plaka: return

        self.db.kaydet(plaka, tarih)
        
        search_text = self.search_input.text().upper().strip()
        self.table.insertRow(0)
        self.table.setItem(0, 0, QTableWidgetItem(plaka))
        self.table.setItem(0, 1, QTableWidgetItem(durum))
        self.table.setItem(0, 2, QTableWidgetItem(tarih))
        
        if search_text and search_text not in plaka.upper():
            self.table.setRowHidden(0, True)

    def update_image(self, qt_img):
        if qt_img is None or qt_img.isNull(): return
        pixmap = QPixmap.fromImage(qt_img)
        scaled = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.FastTransformation)
        self.video_label.setPixmap(scaled)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SmartCampusApp()
    window.showMaximized()
    sys.exit(app.exec_())