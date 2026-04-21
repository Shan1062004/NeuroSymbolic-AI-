# NSEthics-AV: Neuro-Symbolic AI for Multimodal Ethical Reasoning in Autonomous Vehicles

Local, modular MVP that runs entirely on a laptop (Windows/Linux) using open-source models.

## Features
- Video ingestion from uploaded dashcam MP4 or bundled sample clips (OpenCV, configurable FPS sampling)
- Perception with YOLOv8n (Ultralytics) for object detection; simple motion estimation
- Context summarization to concise text for LLM input
- Symbolic Rule Engine for deterministic safety overrides
- Local LLM ethical reasoning (llama-cpp-python with TinyLlama 1.1B Chat GGUF by default)
- Fusion logic combining rules + LLM with audit logs
- FastAPI backend with REST API and optional websocket streaming
- Next.js + Tailwind frontend: split-screen video + decision feed
- Tests and sample scenarios

## Quick Start

### Prereqs
- Python 3.10 or 3.11
- Node.js 18+ and pnpm (or npm/yarn)
- Git (optional)

### Backend Setup (Windows/Linux)
```
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Download a local GGUF model (default: TinyLlama 1.1B Chat):
```
# Creates models/ and downloads TinyLlama
python backend/llm/download_models.py --model tinyllama
```

Run backend:
```
# From repo root
uvicorn backend.server.api:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```
cd frontend
pnpm install
pnpm dev
```
Open http://localhost:3000

## Configuration
- ethics_config.json: thresholds and options for rule engine and fusion
- LLM model selection via env variables or CLI flags:
  - LLM_MODEL_PATH (default models/tinyllama-1.1b-chat.Q5_K_M.gguf)
  - ETHICAL_MODE = Utilitarian | Deontological | Legal | Hybrid

## API Endpoints
- POST /upload_video -> {job_id}
- GET /job_status/{job_id}
- GET /decision_log/{job_id}
- WS /stream_decisions (optional)

## Tests
```
pytest backend/tests -q
```

## Architecture
See docs/architecture.md for module diagram.

## Notes
- YOLOv8 runs on CPU by default; enable CUDA if available.
- LLM is used only for reasoning/explanation. Symbolic rules can override at any time.
- All LLM outputs and final decisions are logged for audit.

