#!/usr/bin/env python3
"""
Clean up downloaded test models
"""
import shutil
import os

cache_dir = "/tmp/qwen-tts-test-models"

print(f"Cleaning up test models from: {cache_dir}")

if os.path.exists(cache_dir):
    try:
        shutil.rmtree(cache_dir)
        print(f"✓ Successfully removed {cache_dir}")
        print(f"Disk space freed: ~3-4 GB")
    except Exception as e:
        print(f"✗ Failed to remove {cache_dir}: {e}")
        print("You may need to remove it manually:")
        print(f"  rm -rf {cache_dir}")
        exit(1)
else:
    print(f"Directory {cache_dir} does not exist (already cleaned up)")
