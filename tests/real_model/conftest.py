"""
Fixtures for real model tests
"""
import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_real_model_env():
    """Load test environment for real models"""
    # Set environment variables for CPU inference
    os.environ["HF_HOME"] = "/tmp/qwen-tts-test-models"
    os.environ["MODEL_CACHE_DIR"] = "/tmp/qwen-tts-test-models"
    os.environ["CUDA_DEVICE"] = "cpu"
    os.environ["USE_FLASH_ATTENTION"] = "false"
    os.environ["API_KEYS"] = "test-api-key"  # Match parent conftest
    os.environ["VOICE_CACHE_ENABLED"] = "true"
    os.environ["AUDIO_PREPROCESSING_ENABLED"] = "true"
    os.environ["ENABLE_PERFORMANCE_LOGGING"] = "true"
    
    yield
    
    # Cleanup happens in cleanup script
