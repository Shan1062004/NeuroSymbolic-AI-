import numpy as np
from backend.perception.yolo_detector import YoloDetector

class DummyYOLO:
    def __init__(self, *args, **kwargs):
        pass
    def predict(self, source, conf=0.25, verbose=False):
        class Box:
            def __init__(self, xyxy, cls, conf):
                self._xyxy = np.array([xyxy], dtype=np.float32)
                self.cls = np.array([cls])
                self.conf = np.array([conf])
            @property
            def xyxy(self):
                return self._xyxy
        class Boxes:
            def __init__(self):
                self._boxes = [
                    Box([100, 200, 140, 320], 0, 0.9),  # person
                    Box([300, 220, 380, 300], 2, 0.8),  # car
                ]
            def __len__(self):
                return len(self._boxes)
            def __getitem__(self, idx):
                return self._boxes[idx]
        class Result:
            def __init__(self):
                self.boxes = Boxes()
        return [Result()]

def test_detection_pipeline_monkeypatch(monkeypatch):
    # Monkeypatch ultralytics.YOLO class inside the module
    monkeypatch.setattr("backend.perception.yolo_detector.YOLO", lambda *args, **kwargs: DummyYOLO())
    det = YoloDetector(conf=0.2)
    frame = np.zeros((360, 640, 3), dtype=np.uint8)
    out = det.detect(frame, frame_id=1, timestamp_ms=33.3)
    labels = [d["label"] for d in out]
    assert "pedestrian" in labels and "vehicle" in labels

