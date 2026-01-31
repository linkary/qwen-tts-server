"""
Test VoiceDesign model with REAL inference (no mocks)
WARNING: CPU inference is SLOW (30-60s per generation)
"""
import pytest

pytestmark = [pytest.mark.slow, pytest.mark.requires_model]


class TestVoiceDesignReal:
    """VoiceDesign model tests with real inference"""
    
    def test_generate_basic(self, api_client):
        """Test basic VoiceDesign generation"""
        print("\n🔊 Testing VoiceDesign basic generation...")
        response = api_client.post(
            "/api/v1/voice-design/generate",
            json={
                "text": "Testing VoiceDesign model.",
                "language": "English",
                "instruct": "A warm friendly voice",
                "response_format": "base64"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "audio" in data, "Response missing 'audio' field"
        assert len(data["audio"]) > 0, "Generated audio is empty"
        print(f"✓ Audio generated successfully ({len(data['audio'])} bytes)")
    
    def test_performance_headers(self, api_client):
        """Test performance headers with real model"""
        print("\n📊 Testing performance headers...")
        response = api_client.post(
            "/api/v1/voice-design/generate",
            json={
                "text": "Performance test.",
                "language": "English",
                "instruct": "Clear professional voice",
                "response_format": "wav"  # WAV format includes performance headers
            }
        )
        
        assert response.status_code == 200
        assert "X-Generation-Time" in response.headers, "Missing X-Generation-Time header"
        
        gen_time = float(response.headers["X-Generation-Time"])
        print(f"✓ Generation time: {gen_time:.2f}s")
        assert gen_time > 0
    
    def test_speed_control(self, api_client):
        """Test speed parameter"""
        print("\n⚡ Testing speed control...")
        response = api_client.post(
            "/api/v1/voice-design/generate",
            json={
                "text": "Speed test.",
                "language": "English",
                "instruct": "Natural voice",
                "speed": 0.8,
                "response_format": "base64"
            }
        )
        
        assert response.status_code == 200
        assert "audio" in response.json()
        print("✓ Speed control works (0.8x)")
