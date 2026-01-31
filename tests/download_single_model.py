#!/usr/bin/env python3
"""
Download a single Qwen3-TTS model for testing
Usage: python tests/download_single_model.py [custom_voice|voice_design|base|tokenizer]
"""
import os
import sys
from huggingface_hub import snapshot_download

# Set cache directory
cache_dir = "/tmp/qwen-tts-test-models"
os.makedirs(cache_dir, exist_ok=True)
os.environ["HF_HOME"] = cache_dir

# Model mapping
models = {
    "custom_voice": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
    "voice_design": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    "base": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
    "tokenizer": "Qwen/Qwen3-TTS-Tokenizer-12Hz",
}

if len(sys.argv) < 2:
    print("Usage: python tests/download_single_model.py [custom_voice|voice_design|base|tokenizer]")
    sys.exit(1)

model_type = sys.argv[1]
if model_type not in models:
    print(f"Error: Unknown model type '{model_type}'")
    print(f"Available: {', '.join(models.keys())}")
    sys.exit(1)

model_id = models[model_type]
print(f"Downloading {model_type}: {model_id}")
print(f"Cache directory: {cache_dir}")
print()

try:
    snapshot_download(repo_id=model_id, cache_dir=cache_dir)
    print(f"✓ {model_id} downloaded successfully")
except Exception as e:
    print(f"✗ Failed to download {model_id}: {e}")
    sys.exit(1)
