"""
Integration tests for Base model API endpoints
"""
import pytest
from unittest.mock import patch


@pytest.mark.integration
@pytest.mark.slow
class TestBaseAPIEndpoints:
    """Test Base model API endpoints"""
    
    def test_clone_endpoint(self, api_client, base64_test_audio, mock_tts_model):
        """Test /api/v1/base/clone endpoint"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Test voice cloning",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text",
                    "response_format": "base64"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "audio" in data
            assert "sample_rate" in data
    
    def test_clone_stream_endpoint(self, api_client, base64_test_audio, mock_tts_model):
        """Test /api/v1/base/clone-stream endpoint"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/base/clone-stream",
                json={
                    "text": "Test streaming",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text"
                }
            )
            
            assert response.status_code == 200
    
    def test_create_prompt_endpoint(self, api_client, base64_test_audio, mock_tts_model):
        """Test /api/v1/base/create-prompt endpoint"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            response = api_client.post(
                "/api/v1/base/create-prompt",
                json={
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "prompt_id" in data
            assert "message" in data
    
    def test_generate_with_prompt_endpoint(self, api_client, base64_test_audio, mock_tts_model):
        """Test /api/v1/base/generate-with-prompt endpoint"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # First create a prompt
            create_response = api_client.post(
                "/api/v1/base/create-prompt",
                json={
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text"
                }
            )
            
            assert create_response.status_code == 200
            prompt_id = create_response.json()["prompt_id"]
            
            # Now generate with that prompt
            gen_response = api_client.post(
                "/api/v1/base/generate-with-prompt",
                json={
                    "text": "New text",
                    "language": "English",
                    "prompt_id": prompt_id,
                    "response_format": "base64"
                }
            )
            
            assert gen_response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
class TestCacheIntegration:
    """Test caching integration with API"""
    
    def test_cache_hit_after_repeated_request(self, api_client, base64_test_audio, mock_tts_model):
        """Test cache hit on repeated requests"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # First request (cache miss)
            response1 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "First request",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text",
                    "response_format": "wav"
                }
            )
            
            assert response1.status_code == 200
            # First request might be cache miss
            cache_status1 = response1.headers.get("X-Cache-Status", "miss")
            
            # Second request with same audio (should be cache hit)
            response2 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Second request",  # Different text
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text",  # Same ref audio and text
                    "response_format": "wav"
                }
            )
            
            assert response2.status_code == 200
            cache_status2 = response2.headers.get("X-Cache-Status", "miss")
            
            # Second request should be cache hit
            assert cache_status2 == "hit", "Second request should hit cache"
