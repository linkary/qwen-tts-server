"""
Streaming utilities for audio generation
"""
import asyncio
import io
import base64
from typing import AsyncIterator, Tuple
import numpy as np
import soundfile as sf


async def stream_audio_chunks(
    audio_data: np.ndarray,
    sample_rate: int,
    chunk_duration: float = 0.5
) -> AsyncIterator[bytes]:
    """
    Stream audio data in chunks
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate in Hz
        chunk_duration: Duration of each chunk in seconds
        
    Yields:
        Audio chunks as bytes
    """
    chunk_samples = int(sample_rate * chunk_duration)
    total_samples = len(audio_data)
    
    for start_idx in range(0, total_samples, chunk_samples):
        end_idx = min(start_idx + chunk_samples, total_samples)
        chunk = audio_data[start_idx:end_idx]
        
        # Convert chunk to WAV bytes
        buffer = io.BytesIO()
        sf.write(buffer, chunk, sample_rate, format="WAV")
        buffer.seek(0)
        
        yield buffer.read()
        
        # Small delay to simulate streaming
        await asyncio.sleep(0.01)


async def stream_audio_base64_chunks(
    audio_data: np.ndarray,
    sample_rate: int,
    chunk_duration: float = 0.5
) -> AsyncIterator[str]:
    """
    Stream audio data as base64 encoded chunks
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate in Hz
        chunk_duration: Duration of each chunk in seconds
        
    Yields:
        Base64 encoded audio chunks
    """
    async for chunk_bytes in stream_audio_chunks(audio_data, sample_rate, chunk_duration):
        yield base64.b64encode(chunk_bytes).decode("utf-8")


def create_sse_message(data: str, event: str = "audio") -> str:
    """
    Create Server-Sent Events message
    
    Args:
        data: Data to send
        event: Event type
        
    Returns:
        Formatted SSE message
    """
    return f"event: {event}\ndata: {data}\n\n"
