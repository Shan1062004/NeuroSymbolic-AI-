import cv2
import os
from typing import Generator, Optional, Dict

class VideoIngest:
    def __init__(self, video_path: str, output_frames_dir: str, target_fps: int = 3):
        self.video_path = video_path
        self.output_frames_dir = output_frames_dir
        os.makedirs(self.output_frames_dir, exist_ok=True)
        self.target_fps = target_fps

    def frames(self) -> Generator[Dict, None, None]:
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video: {self.video_path}")
        src_fps = cap.get(cv2.CAP_PROP_FPS) or 30
        frame_interval = max(int(src_fps // self.target_fps), 1)
        frame_id = 0
        sampled_id = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_id % frame_interval == 0:
                timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
                frame_filename = os.path.join(self.output_frames_dir, f"frame_{sampled_id:06d}.jpg")
                cv2.imwrite(frame_filename, frame)
                yield {
                    "frame_id": sampled_id,
                    "timestamp_ms": timestamp_ms,
                    "frame_path": frame_filename,
                    "frame": frame,
                }
                sampled_id += 1
            frame_id += 1
        cap.release()

