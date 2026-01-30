"""
Integration tests for VoiceDesign API
"""
import pytest
from unittest.mock import patch


@pytest.mark.integration
@pytest.mark.slow
class TestVoiceDesignAPI:
    """Test VoiceDesign API endpoints"""
    
    def test_generate_endpoint(self, api_client, mock_tts_model):
        """Test /api/v1/voice-design/generate"""
        with patch('app.models.manager.model_manager.get_voice_design_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/voice-design/generate",
                json={
                    "text": "Voice design test",
                    "language": "English",
                    "instruct": "A warm professional female voice",
                    "response_format": "base64"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "audio" in data
            assert "sample_rate" in data
    
    def test_generate_stream_endpoint(self, api_client, mock_tts_model):
        """Test /api/v1/voice-design/generate-stream"""
        with patch('app.models.manager.model_manager.get_voice_design_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/voice-design/generate-stream",
                json={
                    "text": "Streaming voice design",
                    "language": "English",
                    "instruct": "Deep calm male voice"
                }
            )
            
            assert response.status_code == 200
    
    def test_performance_headers(self, api_client, mock_tts_model):
        """Test VoiceDesign includes performance headers"""
        with patch('app.models.manager.model_manager.get_voice_design_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/voice-design/generate",
                json={
                    "text": "Performance test",
                    "language": "English",
                    "instruct": "Clear voice",
                    "response_format": "wav"
                }
            )
            
            assert response.status_code == 200
            assert "X-Generation-Time" in response.headers
