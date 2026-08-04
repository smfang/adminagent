"""
Modal deployment recipe for GuardReasoner.
Adapted from COPE evaluation's serve pattern.

Usage:
    modal secret create guardreasoner-secrets HF_TOKEN=hf_... VLLM_API_KEY=sk-...
    modal deploy scripts/serve_guardreasoner.py
"""

import modal

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
MODEL_NAME = "GuardReasoner/GardReasoner-8B"  # or variant from HF
GPU_CONFIG = "H100:1"          # 8B model fits on A100:1 or L40S:1 too
MAX_MODEL_LEN = 8192           # GuardReasoner 8B context window
SECRET_NAME = "guardreasoner-secrets"

# ------------------------------------------------------------------
# Image
# ------------------------------------------------------------------
image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("git")
    .pip_install(
        "vllm>=0.5.0",
        "huggingface_hub",
        "hf-transfer",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
)

# ------------------------------------------------------------------
# Volume (caches model weights between runs)
# ------------------------------------------------------------------
hf_cache = modal.Volume.from_name("guardreasoner-hf-cache", create_if_missing=True)

# ------------------------------------------------------------------
# App
# ------------------------------------------------------------------
app = modal.App("guardreasoner-serve", image=image)


@app.function(
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=[modal.Secret.from_name(SECRET_NAME)],
    timeout=1800,
)
def download_model():
    """Pre-download weights to persistent volume (one-time, ~$0.01)."""
    import os
    import subprocess

    token = os.environ["HF_TOKEN"]
    subprocess.run(
        [
            "huggingface-cli", "download",
            MODEL_NAME,
            "--token", token,
            "--local-dir", "/root/.cache/huggingface/guardreasoner",
        ],
        check=True,
    )
    print("Model downloaded.")


@app.function(
    gpu=GPU_CONFIG,
    volumes={"/root/.cache/huggingface": hf_cache},
    secrets=[modal.Secret.from_name(SECRET_NAME)],
    timeout=600,
    scaledown_window=600,  # 10 min idle before spin-down
)
@modal.web_server(port=8000, startup_timeout=300)
def serve():
    """vLLM serving endpoint."""
    import os
    import subprocess

    token = os.environ["HF_TOKEN"]
    api_key = os.environ["VLLM_API_KEY"]

    cmd = [
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", MODEL_NAME,
        "--host", "0.0.0.0",
        "--port", "8000",
        "--max-model-len", str(MAX_MODEL_LEN),
        "--api-key", api_key,
        # GuardReasoner may need trust-remote-code; check model card
        # "--trust-remote-code",
    ]

    # If model was pre-downloaded, vLLM will find it in the cache
    subprocess.Popen(cmd)
