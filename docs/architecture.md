# Architecture Overview

Components:
- Video Ingest (OpenCV) -> frames
- YOLOv8n Detector -> detections per frame
- Context Generator -> text summary
- Symbolic Engine -> overrides/flags
- LLM Ethics Agent (llama-cpp) -> JSON reasoning
- Decision Fusion -> final decision
- FastAPI -> endpoints
- Frontend (Next.js) -> upload + split view

Data Flow:
Video -> Frames -> Detections -> Summary -> {Rules, LLM} -> Fusion -> Logs

