from typing import List, Dict, Any
import math

class ContextGenerator:
    def __init__(self, lane_id: str = "center"):
        self.lane_id = lane_id

    @staticmethod
    def distance_approx(bbox):
        x1, y1, x2, y2 = bbox
        height = max(y2 - y1, 1.0)
        return round(100.0 / height, 2)  # rough heuristic in meters

    def summarize(self, frame_id: int, ego_speed_kmh: float, detections: List[Dict[str, Any]], weather: str = "clear") -> str:
        counts = {}
        closest_obj = None
        closest_dist = float('inf')
        for d in detections:
            lbl = d["label"]
            counts[lbl] = counts.get(lbl, 0) + 1
            dist = self.distance_approx(d["bbox"])  # meters approx
            if dist < closest_dist:
                closest_dist = dist
                closest_obj = d
        parts = [f"Frame {frame_id} — "]
        if closest_obj:
            parts.append(f"closest {closest_obj['label']} at {closest_dist}m, conf {closest_obj['confidence']:.2f}")
        if counts:
            counts_str = ", ".join([f"{k}:{v}" for k,v in counts.items()])
            parts.append(f"; counts: {counts_str}")
        parts.append(f"; speed {ego_speed_kmh:.1f} km/h; lane {self.lane_id}; weather {weather}")
        return "".join(parts)

