from ultralytics import YOLO
import torch

def train_final():
    # GPU kontrolü - RTX 4050'yi yakalayalım
    device = 0 if torch.cuda.is_available() else "cpu"
    print(f"🚀 Canavar uyandı! Eğitim şunun üzerinde yapılacak: {device}")

    # Modeli yükle
    model = YOLO('yolov8n.pt')

    # 100 Epochluk gerçek eğitim
    # workers=0 veya 2 yaparak Windows'un çökmesini engelliyoruz
    results = model.train(
        data='data/data.yaml', 
        epochs=100, 
        imgsz=640, 
        device=device,
        batch=16,
        workers=2, 
        name='campus_anpr_final'
    )

# Windows'ta multiprocessing hatasını engelleyen o meşhur blok:
if __name__ == '__main__':
    train_final()