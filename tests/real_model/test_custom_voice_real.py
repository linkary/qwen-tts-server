"""
Test CustomVoice model with REAL inference (no mocks)
WARNING: CPU inference is SLOW (30-60s per generation)
"""
import pytest

pytestmark = [pytest.mark.slow, pytest.mark.requires_model]


class TestCustomVoiceReal:
    """CustomVoice model tests with real inference"""
    
    def test_generate_basic(self, api_client):
        """Test basic CustomVoice generation"""
        print("\n🔊 Testing CustomVoice basic generation...")
        response = api_client.post(
            "/api/v1/custom-voice/generate",
            json={
                "text": "Testing CustomVoice model with real inference.",
                "language": "English",
                "speaker": "Ryan",
                "response_format": "base64"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "audio" in data, "Response missing 'audio' field"
        assert len(data["audio"]) > 0, "Generated audio is empty"
        print(f"✓ Audio generated successfully ({len(data['audio'])} bytes)")
    
    def test_performance_metrics(self, api_client):
        """Test performance tracking with real model"""
        print("\n📊 Testing performance metrics...")
        response = api_client.post(
            "/api/v1/custom-voice/generate",
            json={
                "text": "Testing performance metrics.",
                "language": "English",
                "speaker": "Ryan",
                "response_format": "wav"  # WAV format includes performance headers
            }
        )
        
        assert response.status_code == 200
        
        # Verify performance headers
        assert "X-Generation-Time" in response.headers, "Missing X-Generation-Time header"
        assert "X-RTF" in response.headers, "Missing X-RTF header"
        
        gen_time = float(response.headers["X-Generation-Time"])
        rtf = float(response.headers["X-RTF"])
        
        print(f"✓ Generation time: {gen_time:.2f}s")
        print(f"✓ RTF: {rtf:.3f}")
        
        assert gen_time > 0, "Generation time should be positive"
        assert rtf > 0, "RTF should be positive"
    
    def test_speed_control(self, api_client):
        """Test speed parameter with real model"""
        print("\n⚡ Testing speed control...")
        response = api_client.post(
            "/api/v1/custom-voice/generate",
            json={
                "text": "Speed test.",
                "language": "English",
                "speaker": "Ryan",
                "speed": 1.5,
                "response_format": "base64"
            }
        )
        
        assert response.status_code == 200, f"Speed control failed: {response.text}"
        assert "audio" in response.json()
        print("✓ Speed control works (1.5x)")
