"""
Audio processing utilities
"""
import io
import base64
import tempfile
from typing import Tuple, Union, Optional
import numpy as np
import soundfile as sf
import aiofiles
import httpx


async def load_audio_from_url(url: str) -> Tuple[np.ndarray, int]:
    """
    Load audio from URL
    
    Args:
        url: URL to audio file
        
    Returns:
        Tuple of (audio_data, sample_rate)
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        # Save to temporary file and load with soundfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(response.content)
            tmp.flush()
            audio_data, sample_rate = sf.read(tmp.name)
        
        return audio_data, sample_rate


def load_audio_from_base64(base64_str: str) -> Tuple[np.ndarray, int]:
    """
    Load audio from base64 string
    
    Args:
        base64_str: Base64 encoded audio data
        
    Returns:
        Tuple of (audio_data, sample_rate)
    """
    # Remove data URL prefix if present
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    
    audio_bytes = base64.b64decode(base64_str)
    audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
    
    return audio_data, sample_rate


async def load_audio_from_file(file_content: bytes) -> Tuple[np.ndarray, int]:
    """
    Load audio from uploaded file content
    
    Args:
        file_content: Raw file bytes
        
    Returns:
        Tuple of (audio_data, sample_rate)
    """
    audio_data, sample_rate = sf.read(io.BytesIO(file_content))
    return audio_data, sample_rate


def numpy_to_wav_bytes(audio_data: np.ndarray, sample_rate: int) -> bytes:
    """
    Convert numpy array to WAV bytes
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate in Hz
        
    Returns:
        WAV file bytes
    """
    buffer = io.BytesIO()
    sf.write(buffer, audio_data, sample_rate, format="WAV")
    buffer.seek(0)
    return buffer.read()


def numpy_to_base64(audio_data: np.ndarray, sample_rate: int) -> str:
    """
    Convert numpy array to base64 encoded WAV
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate in Hz
        
    Returns:
        Base64 encoded WAV data
    """
    wav_bytes = numpy_to_wav_bytes(audio_data, sample_rate)
    return base64.b64encode(wav_bytes).decode("utf-8")


async def prepare_ref_audio(
    ref_audio_url: Optional[str] = None,
    ref_audio_base64: Optional[str] = None,
    ref_audio_file: Optional[bytes] = None,
) -> Optional[Tuple[np.ndarray, int]]:
    """
    Prepare reference audio from various sources
    
    Args:
        ref_audio_url: URL to reference audio
        ref_audio_base64: Base64 encoded reference audio
        ref_audio_file: Raw file bytes
        
    Returns:
        Tuple of (audio_data, sample_rate) or None
    """
    if ref_audio_url:
        return await load_audio_from_url(ref_audio_url)
    elif ref_audio_base64:
        return load_audio_from_base64(ref_audio_base64)
    elif ref_audio_file:
        return await load_audio_from_file(ref_audio_file)
    
    return None
