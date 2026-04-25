import easyocr
import cv2
import re
# OCR okuyucusunu hazırla (Türkçe ve İngilizce karakterler için)
reader = easyocr.Reader(['tr', 'en'])

# TEST: Buraya elindeki bir plaka resminin yolunu yaz
# (Veya data/test/images klasöründen bir tane seç)
image_path = 'data/test/images/116_jpg.rf.24785ec416fcc5c6bdeb22815143df9d.jpg' 

# Resmi oku
image = cv2.imread(image_path)

# EasyOCR ile metni oku
results = reader.readtext(image)

print("-" * 30)
print("OKUMA SONUÇLARI:")
# ocr_test.py içindeki döngü kısmını şunla değiştir:
full_plate = ""
for (bbox, text, prob) in results:
    # Sadece Alfanümerik (Harf ve Rakam) karakterleri tut
    clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
    full_plate += clean_text

print(f"Final Okunan Plaka: {full_plate}")