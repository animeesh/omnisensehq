import cv2
import sqlite3
import torch
from pathlib import Path

# Load YOLOv5 model (you can use 'yolov5s', 'yolov5m', etc.)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

# Set model to eval mode
model.eval()

# Connect to SQLite DB
conn = sqlite3.connect("detections_yolov5.db")
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        frame_id INTEGER,
        timestamp REAL,
        label TEXT,
        confidence REAL,
        x INTEGER,
        y INTEGER,
        w INTEGER,
        h INTEGER
    )
''')

conn.commit()

# Load the video
#video_path = 0  # Replace with your path
cap = cv2.VideoCapture(0)
frame_id = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1
    timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0  # seconds

    # Run YOLOv5 on the frame (returns tensor results)
    results = model(frame)
    detections = results.xyxy[0]  # xyxy format

    for *xyxy, conf, cls in detections:
        x1, y1, x2, y2 = map(int, xyxy)
        w = x2 - x1
        h = y2 - y1
        label = model.names[int(cls)]

        cursor.execute('''
            INSERT INTO detections (frame_id, timestamp, label, confidence, x, y, w, h)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (frame_id, timestamp, label, float(conf), x1, y1, w, h))
        conn.commit()

    #Optional: Show detections (for debugging)
    results.render()
    cv2.imshow("YOLOv5 Detection", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
conn.close()
cv2.destroyAllWindows()
