param(
  [string]$HostIP = "127.0.0.1",
  [int]$Port = 8000
)

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r backend\requirements.txt
python backend\llm\download_models.py --model tinyllama
uvicorn backend.server.api:app --host $HostIP --port $Port --reload

