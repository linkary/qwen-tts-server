"""
Pytest configuration and shared fixtures
"""
import pytest
import os
import tempfile
import numpy as np
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from tests.utils import (
    generate_test_audio,
    add_silence,
    create_stereo_audio,
    save_test_audio
)


# Configure test environment
os.environ["VOICE_CACHE_ENABLED"] = "true"
os.environ["AUDIO_PREPROCESSING_ENABLED"] = "true"
os.environ["ENABLE_PERFORMANCE_LOGGING"] = "true"
os.environ["API_KEYS"] = "test-api-key"


@pytest.fixture(scope="session")
def test_audio_samples() -> Dict[str, tuple]:
    """
    Generate test audio samples for all tests
    
    Returns:
        Dictionary mapping sample name to (audio_data, sample_rate) tuple
    """
    samples = {}
    sample_rate = 24000
    
    # Short clean audio (3s)
    samples["short_clean"] = (
        generate_test_audio(duration=3.0, sample_rate=sample_rate),
        sample_rate
    )
    
    # Long audio (30s)
    samples["long"] = (
        generate_test_audio(duration=30.0, sample_rate=sample_rate),
        sample_rate
    )
    
    # Audio with silent edges
    audio = generate_test_audio(duration=5.0, sample_rate=sample_rate)
    audio_with_silence = add_silence(audio, sample_rate, 2.0, position='both')
    samples["silent_edges"] = (audio_with_silence, sample_rate)
    
    # Audio with pauses
    audio1 = generate_test_audio(duration=5.0, sample_rate=sample_rate)
    silence = np.zeros(int(1.0 * sample_rate), dtype=np.float32)
    audio2 = generate_test_audio(duration=5.0, sample_rate=sample_rate, frequency=550.0)
    audio_with_pauses = np.concatenate([audio1, silence, audio2, silence, audio1])
    samples["with_pauses"] = (audio_with_pauses, sample_rate)
    
    # Stereo audio
    audio = generate_test_audio(duration=3.0, sample_rate=sample_rate)
    samples["stereo"] = (create_stereo_audio(audio), sample_rate)
    
    # Noisy audio
    samples["noisy"] = (
        generate_test_audio(duration=3.0, sample_rate=sample_rate, add_noise=True, noise_level=0.05),
        sample_rate
    )
    
    # Silent audio
    samples["silent"] = (
        np.zeros(3 * sample_rate, dtype=np.float32),
        sample_rate
    )
    
    # Very short audio (0.5s)
    samples["very_short"] = (
        generate_test_audio(duration=0.5, sample_rate=sample_rate),
        sample_rate
    )
    
    # Medium audio (10s) - within target range
    samples["medium"] = (
        generate_test_audio(duration=10.0, sample_rate=sample_rate),
        sample_rate
    )
    
    # Continuous speech without pauses (20s)
    audio = np.zeros(20 * sample_rate, dtype=np.float32)
    np.random.seed(42)
    for i in range(100):
        freq = 200 + np.random.random() * 600
        start = int(i * 0.2 * sample_rate)
        end = int((i * 0.2 + 0.2) * sample_rate)
        if end > len(audio):
            break
        segment = generate_test_audio(duration=0.2, sample_rate=sample_rate, frequency=freq)
        # Ensure segment length matches slice length
        slice_len = end - start
        if len(segment) > slice_len:
            segment = segment[:slice_len]
        elif len(segment) < slice_len:
            # Pad with zeros if needed
            segment = np.pad(segment, (0, slice_len - len(segment)), mode='constant')
        audio[start:end] = segment
    samples["continuous"] = (audio, sample_rate)
    
    return samples


@pytest.fixture
def temp_audio_file(test_audio_samples):
    """
    Create a temporary audio file for testing
    
    Yields:
        Path to temporary audio file
    """
    audio, sample_rate = test_audio_samples["short_clean"]
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        save_test_audio(audio, sample_rate, tmp.name)
        yield tmp.name
        # Cleanup
        try:
            os.unlink(tmp.name)
        except:
            pass


@pytest.fixture
def temp_long_audio_file(test_audio_samples):
    """
    Create a temporary long audio file for testing preprocessing
    
    Yields:
        Path to temporary audio file
    """
    audio, sample_rate = test_audio_samples["long"]
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        save_test_audio(audio, sample_rate, tmp.name)
        yield tmp.name
        # Cleanup
        try:
            os.unlink(tmp.name)
        except:
            pass


@pytest.fixture
def api_client():
    """
    FastAPI test client with authentication
    
    Returns:
        TestClient instance
    """
    from app.main import app
    
    client = TestClient(app)
    # Add default API key header
    client.headers = {"X-API-Key": "test-api-key"}
    
    return client


@pytest.fixture
def mock_tts_model():
    """
    Mock TTS model for unit tests
    
    Returns:
        Mock model object
    """
    model = MagicMock()
    
    # Mock generate_custom_voice
    def mock_generate_custom_voice(text, language, speaker, instruct=""):
        sample_rate = 24000
        duration = len(text) * 0.05  # ~0.05s per character
        audio = generate_test_audio(duration=duration, sample_rate=sample_rate)
        return [audio], sample_rate
    
    model.generate_custom_voice = Mock(side_effect=mock_generate_custom_voice)
    
    # Mock generate_voice_design
    def mock_generate_voice_design(text, language, instruct):
        sample_rate = 24000
        duration = len(text) * 0.05
        audio = generate_test_audio(duration=duration, sample_rate=sample_rate)
        return [audio], sample_rate
    
    model.generate_voice_design = Mock(side_effect=mock_generate_voice_design)
    
    # Mock generate_voice_clone
    def mock_generate_voice_clone(text, language, voice_clone_prompt=None, ref_audio=None, ref_text=None, x_vector_only_mode=False):
        sample_rate = 24000
        duration = len(text) * 0.05
        audio = generate_test_audio(duration=duration, sample_rate=sample_rate)
        return [audio], sample_rate
    
    model.generate_voice_clone = Mock(side_effect=mock_generate_voice_clone)
    
    # Mock create_voice_clone_prompt
    model.create_voice_clone_prompt = Mock(return_value={"prompt": "mock_prompt"})
    
    return model


@pytest.fixture
def sample_ref_audio():
    """
    Sample reference audio for voice cloning tests
    
    Returns:
        Tuple of (audio_data, sample_rate, ref_text)
    """
    sample_rate = 24000
    audio = generate_test_audio(duration=3.0, sample_rate=sample_rate)
    ref_text = "This is a sample reference audio for testing."
    
    return audio, sample_rate, ref_text


@pytest.fixture(autouse=True)
def reset_cache():
    """
    Reset voice cache before each test
    """
    from app.utils.caching import get_voice_cache
    
    try:
        cache = get_voice_cache()
        cache.clear()
        cache.reset_stats()
    except:
        pass  # Cache might not be initialized yet
    
    yield


@pytest.fixture
def mock_settings():
    """
    Mock settings for testing
    
    Returns:
        Mock settings object
    """
    from unittest.mock import Mock
    
    settings = Mock()
    settings.voice_cache_enabled = True
    settings.voice_cache_max_size = 100
    settings.voice_cache_ttl_seconds = 3600
    settings.audio_preprocessing_enabled = True
    settings.ref_audio_max_duration = 15.0
    settings.ref_audio_target_duration_min = 5.0
    settings.audio_upload_max_size_mb = 5.0
    settings.audio_upload_max_duration = 60.0
    settings.enable_performance_logging = True
    settings.enable_warmup = False  # Disable for faster tests
    
    return settings


@pytest.fixture
def base64_test_audio(test_audio_samples):
    """
    Base64 encoded test audio for API tests
    
    Returns:
        Base64 encoded audio string
    """
    import base64
    import io
    import soundfile as sf
    
    audio, sample_rate = test_audio_samples["short_clean"]
    
    buffer = io.BytesIO()
    sf.write(buffer, audio, sample_rate, format='WAV')
    buffer.seek(0)
    
    return base64.b64encode(buffer.read()).decode('utf-8')
