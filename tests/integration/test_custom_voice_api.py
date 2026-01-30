"""
Integration tests for CustomVoice API
"""
import pytest
from unittest.mock import patch


@pytest.mark.integration
@pytest.mark.slow
class TestCustomVoiceAPI:
    """Test CustomVoice API endpoints"""
    
    def test_generate_endpoint(self, api_client, mock_tts_model):
        """Test /api/v1/custom-voice/generate"""
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/custom-voice/generate",
                json={
                    "text": "Hello world",
                    "language": "English",
                    "speaker": "Ryan",
                    "response_format": "base64"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "audio" in data
            assert "sample_rate" in data
    
    def test_generate_with_instruct(self, api_client, mock_tts_model):
        """Test CustomVoice with instruct parameter"""
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/custom-voice/generate",
                json={
                    "text": "Happy voice test",
                    "language": "English",
                    "speaker": "Ryan",
                    "instruct": "Very happy and energetic",
                    "response_format": "base64"
                }
            )
            
            assert response.status_code == 200
    
    def test_generate_stream_endpoint(self, api_client, mock_tts_model):
        """Test /api/v1/custom-voice/generate-stream"""
        with patch('app.models.manager.model_manager.get_custom_voice_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/custom-voice/generate-stream",
                json={
                    "text": "Streaming test",
                    "language": "English",
                    "speaker": "Aiden"
                }
            )
            
            assert response.status_code == 200
    
    def test_speakers_endpoint(self, api_client):
        """Test /api/v1/custom-voice/speakers"""
        response = api_client.get("/api/v1/custom-voice/speakers")
        
        assert response.status_code == 200
        data = response.json()
        assert "speakers" in data
        assert len(data["speakers"]) > 0
    
    def test_languages_endpoint(self, api_client):
        """Test /api/v1/custom-voice/languages"""
        response = api_client.get("/api/v1/custom-voice/languages")
        
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "English" in data["languages"]
        assert "Auto" in data["languages"]
