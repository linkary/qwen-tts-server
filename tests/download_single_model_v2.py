#!/usr/bin/env python3
"""
Download a single Qwen3-TTS model for testing (with better progress display)
Usage: python tests/download_single_model_v2.py [custom_voice|voice_design|base|tokenizer]
"""
import os
import sys

# Set cache directory BEFORE importing huggingface_hub
cache_dir = "/tmp/qwen-tts-test-models"
os.makedirs(cache_dir, exist_ok=True)
os.environ["HF_HOME"] = cache_dir
os.environ["TRANSFORMERS_CACHE"] = cache_dir

from huggingface_hub import hf_hub_download
import time

# Model mapping
models = {
    "custom_voice": ("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", [
        "config.json",
        "generation_config.json",
        "model.safetensors",
        "model.safetensors.index.json",
        "preprocessor_config.json",
        "tokenizer_config.json",
        "vocab.json",
        "merges.txt",
    ]),
    "voice_design": ("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", [
        "config.json",
        "generation_config.json",
        "model.safetensors",
        "model.safetensors.index.json",
        "preprocessor_config.json",
        "tokenizer_config.json",
        "vocab.json",
        "merges.txt",
    ]),
    "base": ("Qwen/Qwen3-TTS-12Hz-1.7B-Base", [
        "config.json",
        "generation_config.json",
        "model.safetensors",
        "model.safetensors.index.json",
        "preprocessor_config.json",
        "tokenizer_config.json",
        "vocab.json",
        "merges.txt",
    ]),
    "tokenizer": ("Qwen/Qwen3-TTS-Tokenizer-12Hz", [
        "config.json",
        "merges.txt",
        "tokenizer_config.json",
        "vocab.json",
    ]),
}

if len(sys.argv) < 2:
    print("Usage: python tests/download_single_model_v2.py [custom_voice|voice_design|base|tokenizer]")
    sys.exit(1)

model_type = sys.argv[1]
if model_type not in models:
    print(f"Error: Unknown model type '{model_type}'")
    print(f"Available: {', '.join(models.keys())}")
    sys.exit(1)

repo_id, files = models[model_type]
print(f"Downloading {model_type}: {repo_id}")
print(f"Cache directory: {cache_dir}")
print(f"Files to download: {len(files)}")
print()

for i, filename in enumerate(files, 1):
    print(f"[{i}/{len(files)}] Downloading {filename}...")
    start = time.time()
    try:
        path = hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=cache_dir)
        elapsed = time.time() - start
        file_size = os.path.getsize(path) / (1024 * 1024)  # MB
        print(f"  ✓ Downloaded ({file_size:.1f} MB in {elapsed:.1f}s)")
    except Exception as e:
        # Some files might not exist (e.g., index.json for non-sharded models)
        if "404" in str(e) or "Entry Not Found" in str(e):
            print(f"  ⊘ Skipped (file doesn't exist)")
        else:
            print(f"  ✗ Failed: {e}")
            sys.exit(1)

print()
print(f"✓ {repo_id} downloaded successfully")
print(f"Models cached in: {cache_dir}")
