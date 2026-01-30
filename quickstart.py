#!/usr/bin/env python3
"""
Quick start script to test the Qwen3-TTS API server
"""
import requests
import sys
import time

BASE_URL = "http://localhost:8000"

def check_server():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is running (version: {data['version']})")
            return True
    except requests.exceptions.RequestException:
        pass
    
    print("✗ Server is not running")
    print(f"  Please start the server first:")
    print(f"  - Local: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print(f"  - Docker: docker-compose up -d")
    return False


def main():
    print("Qwen3-TTS API Server - Quick Start Check\n")
    
    if not check_server():
        sys.exit(1)
    
    print("\nServer is ready! You can now:")
    print(f"  - View API docs: {BASE_URL}/docs")
    print(f"  - View ReDoc: {BASE_URL}/redoc")
    print(f"  - Run tests: python test_api.py")
    print(f"\nExample curl command:")
    print(f"""
  curl -X POST {BASE_URL}/api/v1/custom-voice/generate \\
    -H "X-API-Key: your-api-key-1" \\
    -H "Content-Type: application/json" \\
    -d '{{"text": "Hello world", "language": "English", "speaker": "Ryan"}}' \\
    --output test.wav
    """)


if __name__ == "__main__":
    main()
