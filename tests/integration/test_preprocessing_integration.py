"""
Integration tests for audio preprocessing with API endpoints
"""
import pytest
import io
import soundfile as sf
from unittest.mock import patch
from tests.utils import generate_test_audio, add_silence


@pytest.mark.integration
@pytest.mark.preprocessing
@pytest.mark.slow
class TestPreprocessingWithBaseAPI:
    """Test preprocessing in voice cloning workflow"""
    
    def test_preprocessing_with_clone_endpoint(self, api_client, base64_test_audio, mock_tts_model):
        """Test preprocessing occurs during voice cloning"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # Create long audio with silence
            audio = generate_test_audio(duration=20.0)
            audio_with_silence = add_silence(audio, 24000, 2.0, position='both')
            
            # Encode to base64
            buffer = io.BytesIO()
            sf.write(buffer, audio_with_silence, 24000, format='WAV')
            buffer.seek(0)
            import base64
            ref_audio_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            
            # Make request
            response = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Test voice cloning with preprocessing",
                    "language": "English",
                    "ref_audio_base64": ref_audio_base64,
                    "ref_text": "Reference audio transcript",
                    "response_format": "wav"
                }
            )
            
            assert response.status_code == 200
            
            # Check performance headers
            assert "X-Generation-Time" in response.headers
            assert "X-Cache-Status" in response.headers
    
    def test_preprocessing_disabled_config(self, api_client, base64_test_audio, mock_tts_model, monkeypatch):
        """Test with AUDIO_PREPROCESSING_ENABLED=false"""
        # Disable preprocessing
        monkeypatch.setenv("AUDIO_PREPROCESSING_ENABLED", "false")
        
        # Need to reload config for changes to take effect
        from importlib import reload
        from app import config
        reload(config)
        
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Test without preprocessing",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text",
                    "response_format": "wav"
                }
            )
            
            # Should still work, just without preprocessing
            assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
class TestCacheStatisticsEndpoint:
    """Test cache statistics endpoint"""
    
    def test_cache_stats_endpoint(self, api_client):
        """Test GET /api/v1/base/cache/stats"""
        response = api_client.get("/api/v1/base/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check expected fields
        assert "enabled" in data
        
        if data["enabled"]:
            assert "size" in data
            assert "max_size" in data
            assert "hits" in data
            assert "misses" in data
            assert "hit_rate_percent" in data
    
    def test_cache_clear_endpoint(self, api_client):
        """Test POST /api/v1/base/cache/clear"""
        response = api_client.post("/api/v1/base/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data


@pytest.mark.integration
@pytest.mark.slow
class TestSpeedControl:
    """Test speed parameter on all endpoints"""
    
    def test_custom_voice_with_speed(self, api_client, mock_tts_model):
        """Test CustomVoice with speed parameter"""
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/custom-voice/generate",
                json={
                    "text": "Testing speed control",
                    "language": "English",
                    "speaker": "Ryan",
                    "speed": 1.5,
                    "response_format": "base64"
                }
            )
            
            assert response.status_code == 200
    
    def test_voice_design_with_speed(self, api_client, mock_tts_model):
        """Test VoiceDesign with speed parameter"""
        with patch('app.models.manager.model_manager.get_voice_design_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/voice-design/generate",
                json={
                    "text": "Testing speed control",
                    "language": "English",
                    "instruct": "Clear professional voice",
                    "speed": 0.8,
                    "response_format": "base64"
                }
            )
            
            assert response.status_code == 200
    
    def test_base_clone_with_speed(self, api_client, base64_test_audio, mock_tts_model):
        """Test Base clone with speed parameter"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Testing speed control",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text",
                    "speed": 2.0,
                    "response_format": "base64"
                }
            )
            
            assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceHeaders:
    """Test performance headers in responses"""
    
    def test_headers_present_in_response(self, api_client, mock_tts_model):
        """Test performance headers are present"""
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/custom-voice/generate",
                json={
                    "text": "Test",
                    "language": "English",
                    "speaker": "Ryan",
                    "response_format": "wav"
                }
            )
            
            assert response.status_code == 200
            
            # Check performance headers
            assert "X-Generation-Time" in response.headers
            assert "X-Cache-Status" in response.headers
            
            # Verify header values are valid
            gen_time = float(response.headers["X-Generation-Time"])
            assert gen_time > 0
            assert response.headers["X-Cache-Status"] in ["hit", "miss"]
    
    def test_rtf_header_calculation(self, api_client, mock_tts_model):
        """Test RTF header is calculated correctly"""
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/custom-voice/generate",
                json={
                    "text": "Testing RTF calculation",
                    "language": "English",
                    "speaker": "Ryan",
                    "response_format": "wav"
                }
            )
            
            if "X-RTF" in response.headers:
                rtf = float(response.headers["X-RTF"])
                assert rtf > 0, "RTF should be positive"
