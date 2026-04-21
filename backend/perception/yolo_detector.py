from typing import List, Dict, Any
import numpy as np
import cv2
import os
from ultralytics import YOLO

LABELS_OF_INTEREST = {
    0: "pedestrian",  # person
    1: "bike",        # bicycle -> bike
    2: "vehicle",     # car
    3: "vehicle",     # motorbike
    5: "vehicle",     # bus
    7: "vehicle",     # truck
    15: "animal",     # cat
    16: "animal",     # dog
    11: "sign",       # stop sign
    9: "sign",        # traffic light
}

class YoloDetector:
    def __init__(self, model_name: str = "yolov8n.pt", conf: float = 0.25, device: str = "cpu"):
        self.model = YOLO(model_name)
        self.conf = conf
        self.device = device
        self.prev_centroids: Dict[int, Dict[int, np.ndarray]] = {}

    def detect(self, frame_bgr: np.ndarray, frame_id: int, timestamp_ms: float) -e List[Dict[str, Any]]:
        results = self.model.predict(source=frame_bgr, conf=self.conf, verbose=False, device=self.device)
        detections: List[Dict[str, Any]] = []
        if not results:
            return detections
        r = results[0]
        boxes = r.boxes
        if boxes is None:
            return detections
        current_centroids: Dict[int, np.ndarray] = {}
        for i in range(len(boxes)):
            b = boxes[i]
            cls_id = int(b.cls.item()) if hasattr(b.cls, 'item') else int(b.cls)
            if cls_id not in LABELS_OF_INTEREST:
                continue
            conf = float(b.conf.item()) if hasattr(b.conf, 'item') else float(b.conf)
            x1, y1, x2, y2 = map(float, b.xyxy[0].tolist())
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            centroid = np.array([cx, cy], dtype=np.float32)
            current_centroids[i] = centroid
            est_speed = 0.0
            if (frame_id - 1) in self.prev_centroids and i in self.prev_centroids[frame_id - 1]:
                prev_c = self.prev_centroids[frame_id - 1][i]
                dt = max((timestamp_ms - self.prev_timestamp_ms), 1.0) / 1000.0
                pixel_delta = float(np.linalg.norm(centroid - prev_c))
                est_speed = pixel_delta / dt  # pixels/sec; downstream can approximate meters
            detections.append({
                "label": LABELS_OF_INTEREST[cls_id],
                "confidence": conf,
                "bbox": [x1, y1, x2, y2],
                "centroid": [float(cx), float(cy)],
                "estimated_speed": float(est_speed)
            })
        self.prev_centroids[frame_id] = current_centroids
        self.prev_timestamp_ms = timestamp_ms
        return detections

