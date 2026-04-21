import os
from PIL import Image, ImageDraw

def generate_frames(out_dir: str, num: int = 30):
    os.makedirs(out_dir, exist_ok=True)
    for i in range(num):
        img = Image.new("RGB", (640, 360), color=(50, 150, 200))
        draw = ImageDraw.Draw(img)
        # draw a moving rectangle to simulate a pedestrian
        x = 50 + i * 5
        y = 200
        draw.rectangle([x, y, x+30, y+80], outline=(255,0,0), width=3)
        img.save(os.path.join(out_dir, f"frame_{i:06d}.jpg"))

if __name__ == "__main__":
    generate_frames("scenarios/sample_videos/frames_synthetic")

