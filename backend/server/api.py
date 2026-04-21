import os
import uuid
from typing import Dict, Any, List
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from ..perception.video_ingest import VideoIngest
from ..perception.yolo_detector import YoloDetector
from ..summarizer.context_generator import ContextGenerator
from ..rules.symbolic_engine import SymbolicEngine
from ..llm.ethics_agent import EthicsAgent
from ..fusion.decision_fusion import DecisionFusion
from ..logger.decision_logger import DecisionLogger
import json
import cv2
from starlette.staticfiles import StaticFiles
import asyncio

app = FastAPI(title="NSEthics-AV")

# Allow local Next.js dev server to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.getcwd(), "runtime")
VIDEOS_DIR = os.path.join(DATA_DIR, "videos")
FRAMES_DIR = os.path.join(DATA_DIR, "frames")
LOGS_DIR = os.path.join(DATA_DIR, "logs")
OVERLAYS_DIR = os.path.join(DATA_DIR, "overlays")
MODELS_DIR = os.path.join(os.getcwd(), "models")
SAMPLES_DIR = os.path.join(os.getcwd(), "scenarios", "sample_videos")
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(OVERLAYS_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=DATA_DIR), name="static")

with open(os.path.join(os.getcwd(), "ethics_config.json"), "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

JOBS: Dict[str, Dict[str, Any]] = {}

class UploadResponse(BaseModel):
    job_id: str

@app.post("/upload_video", response_model=UploadResponse)
def upload_video(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    save_path = os.path.join(VIDEOS_DIR, f"{job_id}.mp4")
    with open(save_path, "wb") as f:
        f.write(file.file.read())
    JOBS[job_id] = {"status": "queued", "video_path": save_path, "clients": [], "queue": asyncio.Queue()}
    return UploadResponse(job_id=job_id)

@app.get("/job_status/{job_id}")
def job_status(job_id: str):
    return JOBS.get(job_id, {"error": "unknown job"})

@app.get("/decision_log/{job_id}")
def decision_log(job_id: str):
    logger = DecisionLogger(LOGS_DIR)
    return JSONResponse(logger.read_all(job_id))

@app.get("/download_log/{job_id}")
def download_log(job_id: str):
    # Return the aggregated decision log as a downloadable JSON file
    logger = DecisionLogger(LOGS_DIR)
    items = logger.read_all(job_id)
    return JSONResponse(items, headers={
        "Content-Disposition": f"attachment; filename=decision_log_{job_id}.json"
    })

@app.get("/samples")
def list_samples():
    files = []
    for name in os.listdir(SAMPLES_DIR):
        if name.lower().endswith(".mp4"):
            files.append(name[:-4])
    return {"samples": sorted(files)}

@app.post("/start_sample/{name}")
def start_sample(name: str):
    mp4 = os.path.join(SAMPLES_DIR, f"{name}.mp4")
    if not os.path.exists(mp4):
        raise HTTPException(status_code=404, detail="Sample not found")
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "video_path": mp4, "clients": [], "queue": asyncio.Queue()}
    return UploadResponse(job_id=job_id)

@app.websocket("/ws/{job_id}")
async def stream_decisions(websocket: WebSocket, job_id: str):
    if job_id not in JOBS:
        await websocket.close()
        return
    await websocket.accept()
    queue: asyncio.Queue = JOBS[job_id]["queue"]
    try:
        while True:
            item = await queue.get()
            await websocket.send_json(item)
    except WebSocketDisconnect:
        pass

@app.post("/process/{job_id}")
def process_job(job_id: str, mode: str | None = None, device: str | None = None):
    job = JOBS.get(job_id)
    if not job:
        return {"error": "unknown job"}
    video_path = job["video_path"]
    JOBS[job_id]["status"] = "processing"

    ingest = VideoIngest(video_path, os.path.join(FRAMES_DIR, job_id), target_fps=int(CONFIG.get("sampling_fps", 3)))
    use_device = (device or os.getenv("YOLO_DEVICE", "cpu")).lower()
    if use_device not in ("cpu", "cuda"):
        use_device = "cpu"
    detector = YoloDetector(conf=float(CONFIG.get("perception", {}).get("min_confidence", 0.25)), device=use_device)
    summarizer = ContextGenerator()
    rules = SymbolicEngine(CONFIG)
    agent = EthicsAgent()
    fusion = DecisionFusion(CONFIG)
    logger = DecisionLogger(LOGS_DIR)

    overlay_dir = os.path.join(OVERLAYS_DIR, job_id)
    os.makedirs(overlay_dir, exist_ok=True)

    ego_speed_kmh = 40.0
    following_m = 15.0
    for sample in ingest.frames():
        frame_id = sample["frame_id"]
        timestamp_ms = sample["timestamp_ms"]
        frame = sample["frame"]
        detections = detector.detect(frame, frame_id, timestamp_ms)
        # draw overlays
        vis = frame.copy()
        for d in detections:
            x1,y1,x2,y2 = map(int, d["bbox"])
            cv2.rectangle(vis, (x1,y1), (x2,y2), (0,255,0), 2)
            label = f"{d['label']} {d['confidence']:.2f}"
            cv2.putText(vis, label, (x1, max(20,y1-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
        overlay_path = os.path.join(overlay_dir, f"frame_{frame_id:06d}.jpg")
        cv2.imwrite(overlay_path, vis)
        overlay_url = f"/static/overlays/{job_id}/frame_{frame_id:06d}.jpg"

        # nearest pedestrian distance
        nearest_ped_dist = None
        for d in detections:
            if d["label"] == "pedestrian":
                dist = ContextGenerator.distance_approx(d["bbox"])  # type: ignore
                if nearest_ped_dist is None or dist < nearest_ped_dist:
                    nearest_ped_dist = dist
        context_summary = summarizer.summarize(frame_id, ego_speed_kmh, detections)
        rule_ctx = {
            "ego_speed_kmh": ego_speed_kmh,
            "nearest_pedestrian_distance_m": nearest_ped_dist,
            "red_light_detected": any(d["label"] == "sign" for d in detections),
            "oncoming_traffic_close": False,
            "steering_maneuver_would_hit_oncoming_lane": False,
        }
        rule_result = rules.evaluate(rule_ctx)
        selected_mode = (mode or CONFIG.get("ethical_mode", "Hybrid"))
        llm_json = agent.reason(context_summary, ego_speed_kmh, "center", following_m, selected_mode)
        fused = fusion.fuse(rule_result, llm_json, detections)
        record = {
            "timestamp_ms": timestamp_ms,
            "frame_id": frame_id,
            "perception_summary": context_summary,
            "detections": detections,
            "symbolic_flags": rule_result.get("flags", []),
            "llm_response": llm_json,
            "final_decision": fused["final_decision"],
            "source": fused["source"],
            "overlay_url": overlay_url
        }
        logger.log(job_id, record)
        # push to websocket queue (non-blocking)
        try:
            JOBS[job_id]["queue"].put_nowait(record)
        except Exception:
            pass
    JOBS[job_id]["status"] = "done"
    return {"status": "done"}

