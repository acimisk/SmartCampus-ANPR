import cv2
from ultralytics import YOLO
import easyocr
import torch
import re

def run_anpr():
    model = YOLO('campus_best.pt') 
    reader = easyocr.Reader(['tr', 'en'], gpu=True) 

    # Orijinal 1080p videon
    cap = cv2.VideoCapture("kampus_test_videosu.mp4") 

    print("🚀 Sistem başlatıldı. Çıkmak için 'q' tuşuna basın.")
    print("-" * 40)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("🎬 Video bitti!")
            break

        # conf=0.5 yaptık tekrar, çünkü artık kalitemiz yüksek
        results = model(frame, stream=True, conf=0.5) 

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                plate_crop = frame[y1:y2, x1:x2]

                if plate_crop.size > 0:
                    ocr_result = reader.readtext(plate_crop)
                    
                    plate_text = ""
                    for (bbox, text, prob) in ocr_result:
                        clean = re.sub(r'[^A-Z0-9]', '', text.upper())
                        plate_text += clean

                    # EĞER PLAKA OKUNDUYSA TERMİNALE YAZDIR!
                    if len(plate_text) > 3: # Çok kısa saçma şeyleri basmasın
                        print(f"🎯 TESPİT EDİLDİ: {plate_text}")

                    # Videonun üzerine çiz
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(frame, f"{plate_text}", (x1, y1 - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

        # 1080p video ekrana sığsın diye boyutunu küçültüyoruz (Sunum için)
        frame_resized = cv2.resize(frame, (1024, 576))
        cv2.imshow("Smart Campus ANPR - Kenan & Ekibi", frame_resized)

        # Videoyu insan gözünün göreceği hıza (yaklaşık 30fps) çektik (1 yerine 30 yaptık)
        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    run_anpr()