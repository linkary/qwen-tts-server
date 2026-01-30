"""
Example test script for the Qwen3-TTS API server
Run with: python test_api.py
"""
import requests
import base64
import sys

# Configuration
API_KEY = "your-api-key-1"  # Change this to match your .env
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoints"""
    print("\n=== Testing Health Endpoints ===")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    print(f"Response: {response.json()}")
    
    response = requests.get(f"{BASE_URL}/health/models")
    print(f"Models health: {response.status_code}")
    print(f"Response: {response.json()}")


def test_custom_voice():
    """Test CustomVoice API"""
    print("\n=== Testing CustomVoice API ===")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # List speakers
    response = requests.get(f"{BASE_URL}/api/v1/custom-voice/speakers", headers=headers)
    print(f"List speakers: {response.status_code}")
    
    # Generate audio
    response = requests.post(
        f"{BASE_URL}/api/v1/custom-voice/generate",
        headers=headers,
        json={
            "text": "Hello, this is a test of the custom voice API.",
            "language": "English",
            "speaker": "Ryan",
            "response_format": "base64"
        }
    )
    print(f"Generate custom voice: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Sample rate: {result['sample_rate']} Hz")
        print(f"Audio data length: {len(result['audio'])} chars")


def test_voice_design():
    """Test VoiceDesign API"""
    print("\n=== Testing VoiceDesign API ===")
    
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/voice-design/generate",
        headers=headers,
        json={
            "text": "Testing voice design with custom characteristics.",
            "language": "English",
            "instruct": "A warm, professional female voice with clear pronunciation",
            "response_format": "base64"
        }
    )
    print(f"Generate voice design: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Sample rate: {result['sample_rate']} Hz")
        print(f"Audio data length: {len(result['audio'])} chars")


def main():
    print("Starting API tests...")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    try:
        test_health()
        test_custom_voice()
        test_voice_design()
        
        print("\n=== All tests completed ===")
        
    except requests.exceptions.ConnectionError:
        print(f"\nError: Could not connect to {BASE_URL}")
        print("Make sure the server is running!")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
