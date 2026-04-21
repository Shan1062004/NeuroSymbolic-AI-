from typing import Dict, Any, List
import os
import orjson

class DecisionLogger:
    def __init__(self, out_dir: str):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

    def log(self, job_id: str, record: Dict[str, Any]):
        path = os.path.join(self.out_dir, f"{job_id}.jsonl")
        with open(path, "ab") as f:
            f.write(orjson.dumps(record))
            f.write(b"\n")

    def read_all(self, job_id: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.out_dir, f"{job_id}.jsonl")
        if not os.path.exists(path):
            return []
        items = []
        with open(path, "rb") as f:
            for line in f:
                items.append(orjson.loads(line))
        return items

