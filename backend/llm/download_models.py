import argparse
import os
import urllib.request

MODELS = {
    "tinyllama": (
        "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat.Q5_K_M.gguf",
        "tinyllama-1.1b-chat.Q5_K_M.gguf",
    ),
    "mistral7b": (
        "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
        "mistral-7b-instruct-v0.2.Q4_K_M.gguf",
    ),
}

def download(model_key: str, out_dir: str = "models"):
    os.makedirs(out_dir, exist_ok=True)
    url, filename = MODELS[model_key]
    out_path = os.path.join(out_dir, filename)
    if os.path.exists(out_path):
        print(f"Model already exists: {out_path}")
        return out_path
    print(f"Downloading {model_key} from {url} ...")
    urllib.request.urlretrieve(url, out_path)
    print(f"Saved to {out_path}")
    return out_path

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=list(MODELS.keys()), default="tinyllama")
    ap.add_argument("--out", default="models")
    args = ap.parse_args()
    download(args.model, args.out)

