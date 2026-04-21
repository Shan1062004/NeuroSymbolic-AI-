#!/usr/bin/env bash
set -euo pipefail
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
# Download default TinyLlama model if missing
python backend/llm/download_models.py --model tinyllama
# Run API server
uvicorn backend.server.api:app --host 127.0.0.1 --port 8000 --reload

