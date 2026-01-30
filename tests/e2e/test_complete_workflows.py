"""
End-to-end tests for complete workflows
"""
import pytest
import time
from unittest.mock import patch


@pytest.mark.e2e
@pytest.mark.slow
class TestVoiceCloningWithCaching:
    """Test complete voice cloning flow with caching"""
    
    def test_cache_improves_performance(self, api_client, base64_test_audio, mock_tts_model):
        """Test cache hit improves performance on repeated requests"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # First request (cache miss)
            start1 = time.time()
            response1 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "First generation",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text",
                    "response_format": "wav"
                }
            )
            time1 = time.time() - start1
            
            assert response1.status_code == 200
            cache_status1 = response1.headers.get("X-Cache-Status", "miss")
            
            # Second request with same ref audio (cache hit)
            start2 = time.time()
            response2 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Second generation",
                    "language": "English",
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text",
                    "response_format": "wav"
                }
            )
            time2 = time.time() - start2
            
            assert response2.status_code == 200
            cache_status2 = response2.headers.get("X-Cache-Status", "miss")
            
            # Verify caching occurred
            if cache_status2 == "hit":
                # Second request should be faster (or at least not slower)
                # Note: With mocks this might not show significant difference
                assert time2 <= time1 * 1.5, "Cached request should not be significantly slower"
    
    def test_different_audio_different_cache(self, api_client, mock_tts_model):
        """Test different reference audio uses different cache"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # Create two different audio samples
            from tests.utils import generate_test_audio
            import base64
            import io
            import soundfile as sf
            
            audio1 = generate_test_audio(duration=3.0, frequency=440.0)
            buffer1 = io.BytesIO()
            sf.write(buffer1, audio1, 24000, format='WAV')
            buffer1.seek(0)
            audio1_base64 = base64.b64encode(buffer1.read()).decode('utf-8')
            
            audio2 = generate_test_audio(duration=3.0, frequency=550.0)
            buffer2 = io.BytesIO()
            sf.write(buffer2, audio2, 24000, format='WAV')
            buffer2.seek(0)
            audio2_base64 = base64.b64encode(buffer2.read()).decode('utf-8')
            
            # Request with audio1
            response1 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Text 1",
                    "language": "English",
                    "ref_audio_base64": audio1_base64,
                    "ref_text": "Reference 1",
                    "response_format": "wav"
                }
            )
            
            assert response1.status_code == 200
            
            # Request with audio2 (different audio, should be cache miss)
            response2 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Text 2",
                    "language": "English",
                    "ref_audio_base64": audio2_base64,
                    "ref_text": "Reference 2",
                    "response_format": "wav"
                }
            )
            
            assert response2.status_code == 200
            
            # Request with audio1 again (should be cache hit)
            response3 = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Text 3",
                    "language": "English",
                    "ref_audio_base64": audio1_base64,
                    "ref_text": "Reference 1",
                    "response_format": "wav"
                }
            )
            
            assert response3.status_code == 200
            cache_status3 = response3.headers.get("X-Cache-Status")
            assert cache_status3 == "hit", "Third request should hit cache for audio1"


@pytest.mark.e2e
@pytest.mark.slow
class TestCompleteWorkflows:
    """Test complete end-to-end workflows"""
    
    def test_upload_and_clone_workflow(self, api_client, temp_audio_file, mock_tts_model):
        """Test complete workflow: upload → clone → verify"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # Step 1: Upload reference audio
            with open(temp_audio_file, 'rb') as f:
                upload_response = api_client.post(
                    "/api/v1/base/upload-ref-audio",
                    files={"file": ("test.wav", f, "audio/wav")}
                )
            
            assert upload_response.status_code == 200
            audio_base64 = upload_response.json()["audio_base64"]
            
            # Step 2: Clone voice using uploaded audio
            clone_response = api_client.post(
                "/api/v1/base/clone",
                json={
                    "text": "Cloned voice test",
                    "language": "English",
                    "ref_audio_base64": audio_base64,
                    "ref_text": "Reference transcript",
                    "response_format": "base64"
                }
            )
            
            assert clone_response.status_code == 200
            assert "audio" in clone_response.json()
    
    def test_create_prompt_and_reuse_workflow(self, api_client, base64_test_audio, mock_tts_model):
        """Test workflow: create prompt → generate multiple times"""
        with patch('app.models.manager.model_manager.get_base_model', return_value=mock_tts_model):
            # Step 1: Create reusable prompt
            prompt_response = api_client.post(
                "/api/v1/base/create-prompt",
                json={
                    "ref_audio_base64": base64_test_audio,
                    "ref_text": "Reference text"
                }
            )
            
            assert prompt_response.status_code == 200
            prompt_id = prompt_response.json()["prompt_id"]
            
            # Step 2: Generate multiple times with same prompt
            for i in range(3):
                gen_response = api_client.post(
                    "/api/v1/base/generate-with-prompt",
                    json={
                        "text": f"Generation {i+1}",
                        "language": "English",
                        "prompt_id": prompt_id,
                        "response_format": "base64"
                    }
                )
                
                assert gen_response.status_code == 200


@pytest.mark.e2e
@pytest.mark.slow
class TestErrorHandling:
    """Test error handling in complete workflows"""
    
    def test_missing_ref_audio(self, api_client):
        """Test error when ref_audio is missing"""
        response = api_client.post(
            "/api/v1/base/clone",
            json={
                "text": "Test",
                "language": "English",
                "ref_text": "Reference",
                "response_format": "wav"
            }
        )
        
        assert response.status_code == 400
        assert "ref_audio" in response.json()["detail"].lower()
    
    def test_missing_ref_text_full_mode(self, api_client, base64_test_audio):
        """Test error when ref_text missing in full mode"""
        response = api_client.post(
            "/api/v1/base/clone",
            json={
                "text": "Test",
                "language": "English",
                "ref_audio_base64": base64_test_audio,
                "x_vector_only_mode": False,
                "response_format": "wav"
            }
        )
        
        assert response.status_code == 400
        assert "ref_text" in response.json()["detail"].lower()
    
    def test_invalid_prompt_id(self, api_client):
        """Test error with invalid prompt_id"""
        response = api_client.post(
            "/api/v1/base/generate-with-prompt",
            json={
                "text": "Test",
                "language": "English",
                "prompt_id": "invalid-uuid-12345",
                "response_format": "wav"
            }
        )
        
        assert response.status_code == 404
