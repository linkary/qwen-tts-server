"""
Test Base voice cloning with REAL inference (no mocks)
WARNING: CPU inference is SLOW (30-60s per generation)
"""
import pytest

pytestmark = [pytest.mark.slow, pytest.mark.requires_model]


class TestBaseCloneReal:
    """Voice cloning tests with real inference"""
    
    def test_clone_basic(self, api_client, base64_test_audio):
        """Test basic voice cloning"""
        print("\n🔊 Testing voice cloning...")
        response = api_client.post(
            "/api/v1/base/clone",
            json={
                "text": "Testing voice cloning with real model.",
                "language": "English",
                "ref_audio_base64": base64_test_audio,
                "ref_text": "This is reference audio for testing.",
                "response_format": "base64"
            }
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "audio" in data, "Response missing 'audio' field"
        assert len(data["audio"]) > 0, "Generated audio is empty"
        print(f"✓ Voice cloned successfully ({len(data['audio'])} bytes)")
    
    def test_preprocessing(self, api_client, base64_test_audio):
        """Test audio preprocessing with real model"""
        print("\n🔧 Testing audio preprocessing...")
        response = api_client.post(
            "/api/v1/base/clone",
            json={
                "text": "Preprocessing test.",
                "language": "English",
                "ref_audio_base64": base64_test_audio,
                "ref_text": "Reference audio.",
                "response_format": "wav"  # WAV format includes headers
            }
        )
        
        assert response.status_code == 200
        assert "X-Cache-Status" in response.headers, "Missing X-Cache-Status header"
        
        cache_status = response.headers["X-Cache-Status"]
        print(f"✓ Cache status: {cache_status}")
        assert cache_status in ["hit", "miss"]
    
    def test_caching(self, api_client, base64_test_audio):
        """Test voice prompt caching with real model"""
        print("\n💾 Testing voice caching...")
        
        # First request - should be cache miss
        print("  Request 1 (expect cache miss)...")
        r1 = api_client.post(
            "/api/v1/base/clone",
            json={
                "text": "First generation for cache test.",
                "language": "English",
                "ref_audio_base64": base64_test_audio,
                "ref_text": "Reference for caching test.",
                "response_format": "wav"  # WAV format includes headers
            }
        )
        
        assert r1.status_code == 200
        cache_status1 = r1.headers.get("X-Cache-Status", "unknown")
        print(f"  Cache status 1: {cache_status1}")
        
        # Second request with same ref audio - should hit cache
        print("  Request 2 (expect cache hit)...")
        r2 = api_client.post(
            "/api/v1/base/clone",
            json={
                "text": "Second generation for cache test.",
                "language": "English",
                "ref_audio_base64": base64_test_audio,
                "ref_text": "Reference for caching test.",  # Same ref
                "response_format": "wav"  # WAV format includes headers
            }
        )
        
        assert r2.status_code == 200
        cache_status2 = r2.headers.get("X-Cache-Status", "unknown")
        print(f"  Cache status 2: {cache_status2}")
        
        # Verify cache hit
        assert cache_status2 == "hit", f"Expected cache hit, got {cache_status2}"
        print("✓ Caching works! Second request hit cache")
    
    def test_speed_control(self, api_client, base64_test_audio):
        """Test speed control with voice cloning"""
        print("\n⚡ Testing speed control with cloning...")
        response = api_client.post(
            "/api/v1/base/clone",
            json={
                "text": "Speed test.",
                "language": "English",
                "ref_audio_base64": base64_test_audio,
                "ref_text": "Reference.",
                "speed": 1.2,
                "response_format": "base64"
            }
        )
        
        assert response.status_code == 200
        assert "audio" in response.json()
        print("✓ Speed control works (1.2x)")
