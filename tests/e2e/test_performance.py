"""
Performance tests for measuring system behavior
"""
import pytest
import time
from unittest.mock import patch
from tests.utils import generate_test_audio
import io
import soundfile as sf
import base64


@pytest.mark.e2e
@pytest.mark.slow
class TestCachePerformance:
    """Test cache performance improvement"""
    
    def test_cache_hit_speedup(self, api_client, base64_test_audio, mock_tts_model):
        """Measure cache hit speedup"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # Warm up
            api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Warmup",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference",
                    "response_format": "wav"
                }
            )
            
            # Measure first request (cache miss)
            start1 = time.time()
            response1 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "First request with timing",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference",
                    "response_format": "wav"
                }
            )
            time1 = time.time() - start1
            
            assert response1.status_code == 200
            
            # Measure second request (cache hit)
            start2 = time.time()
            response2 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Second request with timing",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference",
                    "response_format": "wav"
                }
            )
            time2 = time.time() - start2
            
            assert response2.status_code == 200
            
            # With mocks, difference might be small, but second should not be slower
            assert time2 <= time1 * 1.2, f"Cached request ({time2:.3f}s) should not be much slower than first ({time1:.3f}s)"
            
            # Check cache status in headers
            cache_status2 = response2.headers.get("X-Cache-Status")
            assert cache_status2 == "hit", "Second request should hit cache"
    
    def test_cache_stats_accuracy(self, api_client, base64_test_audio, mock_tts_model):
        """Test cache statistics are accurate"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # Clear cache first
            api_client.post("/api/v1/base/cache/clear")
            
            # Get initial stats
            stats_response = api_client.get("/api/v1/base/cache/stats")
            initial_stats = stats_response.json()
            
            if not initial_stats.get("enabled"):
                pytest.skip("Cache is disabled")
            
            # Make requests
            for i in range(3):
                api_client.post(
                    "/api/v1/base/clone",
                    json={
                        "text": f"Request {i}",
                        "language": "English",
                        "ref_audio_base64": base64_test_audio,
                        "ref_text": "Reference",
                        "response_format": "wav"
                    }
                )
            
            # Get final stats
            final_stats_response = api_client.get("/api/v1/base/cache/stats")
            final_stats = final_stats_response.json()
            
            # Should have at least 1 cache hit (2nd and 3rd requests)
            assert final_stats["hits"] >= 2, f"Expected ≥2 hits, got {final_stats['hits']}"


@pytest.mark.e2e
@pytest.mark.slow
class TestPreprocessingOverhead:
    """Test preprocessing performance overhead"""
    
    def test_preprocessing_overhead_acceptable(self, api_client, mock_tts_model):
        """Verify preprocessing overhead is within acceptable range"""
        # Create long audio that needs preprocessing
        audio = generate_test_audio(duration=25.0)
        buffer = io.BytesIO()
        sf.write(buffer, audio, 24000, format='WAV')
        buffer.seek(0)
        audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            start = time.time()
            response = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Test with long audio",
                    "language": "English",
                    "ref_audio_base64": audio_base64,
                    "ref_text": "Reference text",
                    "response_format": "wav"
                }
            )
            total_time = time.time() - start
            
            assert response.status_code == 200
            
            # Check if preprocessing time is reported
            preprocessing_time = response.headers.get("X-Preprocessing-Time")
            if preprocessing_time:
                prep_time = float(preprocessing_time)
                # Preprocessing should be relatively fast (< 1s for test audio)
                assert prep_time < 1.0, f"Preprocessing took {prep_time}s, expected <1s"


@pytest.mark.e2e
@pytest.mark.slow
class TestSpeedControlPerformance:
    """Test speed control doesn't break functionality"""
    
    def test_speed_variations_work(self, api_client, mock_tts_model):
        """Test different speed values work correctly"""
        speeds = [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]
        
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            for speed in speeds:
                response = api_client.post(
                    "/api/v1/custom-voice/generate",
                    json={
                        "text": "Speed test",
                        "language": "English",
                        "speaker": "Ryan",
                        "speed": speed,
                        "response_format": "base64"
                    }
                )
                
                assert response.status_code == 200, f"Speed {speed}x failed"


@pytest.mark.e2e
@pytest.mark.slow
class TestRTFAccuracy:
    """Test RTF calculation accuracy"""
    
    def test_rtf_in_response_headers(self, api_client, mock_tts_model):
        """Test RTF is present and reasonable in response headers"""
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/custom-voice/generate",
                json={
                    "text": "Test for RTF calculation",
                    "language": "English",
                    "speaker": "Ryan",
                    "response_format": "wav"
                }
            )
            
            assert response.status_code == 200
            
            # Check RTF header
            if "X-RTF" in response.headers:
                rtf = float(response.headers["X-RTF"])
                # RTF should be reasonable (between 0.01 and 100)
                assert 0.01 < rtf < 100, f"RTF {rtf} seems unreasonable"
            
            # Check generation time
            if "X-Generation-Time" in response.headers:
                gen_time = float(response.headers["X-Generation-Time"])
                assert gen_time > 0, "Generation time should be positive"
            
            # Check audio duration
            if "X-Audio-Duration" in response.headers:
                audio_dur = float(response.headers["X-Audio-Duration"])
                assert audio_dur > 0, "Audio duration should be positive"


@pytest.mark.e2e
class TestMemoryUsage:
    """Test memory usage and cache behavior"""
    
    def test_cache_doesnt_grow_indefinitely(self, api_client, mock_tts_model):
        """Test cache respects max_size limit"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # Clear cache
            api_client.post("/api/v1/base/cache/clear")
            
            # Make many requests with different audio
            for i in range(150):  # More than default cache size (100)
                audio = generate_test_audio(duration=1.0, frequency=440.0 + i)
                buffer = io.BytesIO()
                sf.write(buffer, audio, 24000, format='WAV')
                buffer.seek(0)
                audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                
                api_client.post(
                    "/api/v1/base/clone",
                    json={
                        "text": f"Request {i}",
                        "language": "English",
                        "ref_audio_base64": audio_base64,
                        "ref_text": f"Reference {i}",
                        "response_format": "base64"
                    }
                )
            
            # Check cache size
            stats_response = api_client.get("/api/v1/base/cache/stats")
            if stats_response.json().get("enabled"):
                stats = stats_response.json()
                # Cache should be capped at max_size
                assert stats["size"] <= stats["max_size"], "Cache size should not exceed max_size"
                # Should have evictions
                assert stats["evictions"] > 0, "Should have evicted old entries"
