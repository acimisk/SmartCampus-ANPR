# Smart Campus ANPR & Access Control System

This project is an automatic number plate recognition (ANPR) system developed to monitor and manage vehicle traffic at campus entrances and exits. The system detects vehicle plates in real-time from a video stream, converts them to text, and logs them in the database along with the exact second of passage.

Thanks to the developed user interface, a registered plate can be queried in the system, and the video can automatically synchronize to the relevant second when the vehicle passed.

## Core Features
* Dynamic vehicle and plate detection from the video stream using a custom-trained YOLO model.
* Conversion of characters on the plate into text (String) using EasyOCR.
* Real-time comparison of the detected plate against authorized/blacklist records.
* Logging of detected plates along with their access status and time information.
* Modern PyQt5 dashboard featuring live video, recent detection info, and an event table.

## Technologies Used
* **Language:** Python 3.x
* **Image Processing:** OpenCV
* **Object Detection:** YOLO (Ultralytics)
* **Character Recognition:** EasyOCR
* **Database:** MongoDB Atlas
* **GUI:** PyQt5

## Environment Variables
The following variables should be added to the `.env` file:

- `MONGODB_URI`: MongoDB Atlas connection string
- `YOLO_MODEL_PATH` (optional): YOLO model file path (default: `campus_best.pt`)
- `VIDEO_SOURCE` (optional): Video file path or camera index (default: `kampus_test_videosu.mp4`)
- `DETECT_EVERY_N_FRAMES` (optional): YOLO execution interval (default: `1`)
- `OCR_EVERY_N_DETECTIONS` (optional): OCR execution interval (default: `1`)
- `MAX_DETECTION_WIDTH` (optional): Maximum width for detection (default: `1280`)
- `DECISION_LOCK_SECONDS` (optional): Cooldown time to prevent re-logging the same plate (default: `15`)

## Access List Management
To manage authorized and blacklist plates from the terminal:

- Adding:
`python -m database.manage_access_lists add authorized 34ABC123`
- Adding to blacklist:
`python -m database.manage_access_lists add blacklist 06XYZ789`
- Removing from the list:
`python -m database.manage_access_lists remove authorized 34ABC123`
