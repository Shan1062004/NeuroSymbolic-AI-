from typing import Dict, Any
import os
import json
from typing import Optional
from llama_cpp import Llama

SYSTEM_PROMPT = (
    "You are an autonomous-driving ethical advisor. Use concise reasoning, cite detected elements, and prioritize minimizing human harm. "
    "Output a JSON object exactly in the required schema. Never output unstructured text before or after the JSON."
)

USER_TEMPLATE = (
    """
ContextSummary: {context}
EgoVehicleState: {speed_kmh} km/h, lane: {lane}, following_distance: {following}
AvailableActions: ["Brake","SwerveLeft","SwerveRight","SlowDown","Continue","Stop"]
EthicalModes: ["Utilitarian","Deontological","Legal","Hybrid"]
SelectedMode: {mode}
RequestedOutput: Return a JSON with fields:
  - recommended_action (string)
  - ranked_actions (array of {action, score})
  - short_justification (1-2 sentences)
  - detailed_reasoning (3-6 bullet points)
  - confidence (0-1 float)
  - suggested_rule_checks (array of strings)
"""
)

DEFAULT_MODEL = os.getenv("LLM_MODEL_PATH", os.path.join("models", "tinyllama-1.1b-chat.Q5_K_M.gguf"))

class BaseEthicsAgent:
    def reason(self, context_summary: str, speed_kmh: float, lane: str, following_m: float, mode: str = "Hybrid") -
            > Dict[str, Any]:  # pragma: no cover
        raise NotImplementedError

class LlamaCppAgent(BaseEthicsAgent):
    def __init__(self, model_path: str = DEFAULT_MODEL, n_ctx: int = 4096, n_threads: int = 4):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}. Run download_models.py or set LLM_MODEL_PATH.")
        self.llm = Llama(model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, verbose=False)

    def reason(self, context_summary: str, speed_kmh: float, lane: str, following_m: float, mode: str = "Hybrid") -
            > Dict[str, Any]:
        user_msg = USER_TEMPLATE.format(context=context_summary, speed_kmh=speed_kmh, lane=lane, following=following_m, mode=mode)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ]
        out = self.llm.create_chat_completion(messages=messages, temperature=0.2, max_tokens=512)
        content = out["choices"][0]["message"]["content"].strip()
        try:
            data = json.loads(content)
        except Exception:
            start = content.find("{")
            end = content.rfind("}")
            data = json.loads(content[start:end+1])
        return data

class Gpt4AllAgent(BaseEthicsAgent):
    def __init__(self, model_name: Optional[str] = None):
        from gpt4all import GPT4All  # lazy import
        self.model_name = model_name or os.getenv("GPT4ALL_MODEL", "ggml-gpt4all-j-v1.3-groovy")
        self.gpt = GPT4All(self.model_name)

    def reason(self, context_summary: str, speed_kmh: float, lane: str, following_m: float, mode: str = "Hybrid") -
            > Dict[str, Any]:
        prompt = SYSTEM_PROMPT + "\n\n" + USER_TEMPLATE.format(context=context_summary, speed_kmh=speed_kmh, lane=lane, following=following_m, mode=mode)
        out = self.gpt.generate(prompt, temp=0.2, max_tokens=512)
        content = out.strip()
        start = content.find("{")
        end = content.rfind("}")
        return json.loads(content[start:end+1])

class EthicsAgent:
    def __init__(self, backend: str = os.getenv("LLM_BACKEND", "llama_cpp")):
        self.backend = backend
        if backend == "llama_cpp":
            self.agent = LlamaCppAgent()
        elif backend == "gpt4all":
            self.agent = Gpt4AllAgent()
        else:
            raise ValueError(f"Unsupported LLM backend: {backend}")

    def reason(self, *args, **kwargs) -> Dict[str, Any]:
        return self.agent.reason(*args, **kwargs)

