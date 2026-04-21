import os
import cv2
import numpy as np
from PIL import Image, ImageDraw

SCENARIOS = [
    "child_crossing",
    "multiple_pedestrians",
    "adult_vs_animal",
    "red_light",
    "obstacle_on_road",
    "clear_road"
]

COLORS = {
    "pedestrian": (255, 0, 0),
    "vehicle": (0, 255, 0),
    "animal": (255, 165, 0),
    "sign": (0, 0, 255),
}

def draw_box(draw, xy, color):
    draw.rectangle(xy, outline=color, width=3)

def make_video(frames, out_path, fps=6):
    h, w = frames[0].size[1], frames[0].size[0]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    vw = cv2.VideoWriter(out_path, fourcc, fps, (w, h))
    for img in frames:
        arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        vw.write(arr)
    vw.release()

def scenario_child_crossing():
    frames = []
    for i in range(30):
        img = Image.new("RGB", (640, 360), color=(120, 140, 160))
        d = ImageDraw.Draw(img)
        x = 50 + i * 8
        draw_box(d, [x, 220, x+30, 300], COLORS["pedestrian"])
        frames.append(img)
    return frames

def scenario_multiple_pedestrians():
    frames = []
    for i in range(30):
        img = Image.new("RGB", (640, 360), color=(120, 140, 160))
        d = ImageDraw.Draw(img)
        draw_box(d, [100+i*2, 210, 130+i*2, 300], COLORS["pedestrian"])
        draw_box(d, [400-i*2, 210, 430-i*2, 300], COLORS["pedestrian"])
        frames.append(img)
    return frames

def scenario_adult_vs_animal():
    frames = []
    for i in range(30):
        img = Image.new("RGB", (640, 360), color=(120, 140, 160))
        d = ImageDraw.Draw(img)
        draw_box(d, [200, 230, 230, 310], COLORS["pedestrian"])
        draw_box(d, [350+i*3, 260, 380+i*3, 300], COLORS["animal"])
        frames.append(img)
    return frames

def scenario_red_light():
    frames = []
    for i in range(30):
        img = Image.new("RGB", (640, 360), color=(120, 140, 160))
        d = ImageDraw.Draw(img)
        # sign at top-right
        draw_box(d, [560, 40, 600, 80], COLORS["sign"])
        frames.append(img)
    return frames

def scenario_obstacle_on_road():
    frames = []
    for i in range(30):
        img = Image.new("RGB", (640, 360), color=(120, 140, 160))
        d = ImageDraw.Draw(img)
        draw_box(d, [300, 250, 360, 310], (200, 200, 0))
        frames.append(img)
    return frames

def scenario_clear_road():
    frames = []
    for i in range(30):
        img = Image.new("RGB", (640, 360), color=(120, 140, 160))
        frames.append(img)
    return frames

def main(out_dir="scenarios/sample_videos"):
    os.makedirs(out_dir, exist_ok=True)
    scenarios = [
        ("child_crossing", scenario_child_crossing()),
        ("multiple_pedestrians", scenario_multiple_pedestrians()),
        ("adult_vs_animal", scenario_adult_vs_animal()),
        ("red_light", scenario_red_light()),
        ("obstacle_on_road", scenario_obstacle_on_road()),
        ("clear_road", scenario_clear_road()),
    ]
    for name, frames in scenarios:
        out_path = os.path.join(out_dir, f"{name}.mp4")
        make_video(frames, out_path, fps=6)
        print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()

