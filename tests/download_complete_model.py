#!/usr/bin/env python3
"""
Download a complete Qwen3-TTS model with all subdirectories
"""
import os
import sys

# Set cache directory BEFORE imports
cache_dir = "/tmp/qwen-tts-test-models"
os.makedirs(cache_dir, exist_ok=True)
os.environ["HF_HOME"] = cache_dir
os.environ["TRANSFORMERS_CACHE"] = cache_dir

from huggingface_hub import snapshot_download

models = {
    "custom_voice": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "voice_design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    "base": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "tokenizer": "Qwen/Qwen3-TTS-Tokenizer-12Hz",
}

if len(sys.argv) < 2:
    print("Usage: python tests/download_complete_model.py [custom_voice|voice_design|base|tokenizer]")
    sys.exit(1)

model_type = sys.argv[1]
if model_type not in models:
    print(f"Error: Unknown model type '{model_type}'")
    print(f"Available: {', '.join(models.keys())}")
    sys.exit(1)

repo_id = models[model_type]
print(f"Downloading {model_type}: {repo_id}")
print(f"Cache directory: {cache_dir}")
print("This will download ALL files including subdirectories...")
print()

try:
    local_dir = snapshot_download(
        repo_id=repo_id,
        cache_dir=cache_dir,
        resume_download=True,
        local_dir_use_symlinks=True
    )
    print(f"✓ {repo_id} downloaded successfully")
    print(f"Model path: {local_dir}")
except Exception as e:
    print(f"✗ Failed to download {repo_id}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
