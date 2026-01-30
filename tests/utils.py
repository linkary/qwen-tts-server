"""
Test utilities for audio generation and comparison
"""
import numpy as np
import soundfile as sf
from typing import Tuple, Optional, Literal


def generate_test_audio(
    duration: float,
    sample_rate: int = 24000,
    frequency: float = 440.0,
    silence_at: Optional[Tuple[float, float]] = None,
    add_noise: bool = False,
    noise_level: float = 0.01
) -> np.ndarray:
    """
    Generate synthetic audio for testing
    
    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz
        frequency: Tone frequency in Hz
        silence_at: Optional tuple of (start, duration) in seconds for silence insertion
        add_noise: Whether to add noise
        noise_level: Noise level (0.0-1.0)
        
    Returns:
        Audio data as numpy array
    """
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples)
    
    # Generate sine wave
    audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)
    
    # Add silence if specified
    if silence_at:
        silence_start, silence_duration = silence_at
        silence_start_sample = int(silence_start * sample_rate)
        silence_end_sample = int((silence_start + silence_duration) * sample_rate)
        audio[silence_start_sample:silence_end_sample] = 0.0
    
    # Add noise if requested
    if add_noise:
        noise = np.random.normal(0, noise_level, num_samples).astype(np.float32)
        audio = audio + noise
        # Normalize to prevent clipping
        audio = audio / np.max(np.abs(audio))
    
    return audio


def add_silence(
    audio: np.ndarray,
    sample_rate: int,
    duration: float,
    position: Literal['start', 'end', 'both'] = 'both'
) -> np.ndarray:
    """
    Add silence to audio
    
    Args:
        audio: Audio data
        sample_rate: Sample rate in Hz
        duration: Silence duration in seconds
        position: Where to add silence ('start', 'end', 'both')
        
    Returns:
        Audio with added silence
    """
    silence_samples = int(duration * sample_rate)
    silence = np.zeros(silence_samples, dtype=audio.dtype)
    
    if position == 'start':
        return np.concatenate([silence, audio])
    elif position == 'end':
        return np.concatenate([audio, silence])
    else:  # both
        return np.concatenate([silence, audio, silence])


def create_stereo_audio(
    audio: np.ndarray,
    channel_diff: float = 0.0
) -> np.ndarray:
    """
    Convert mono audio to stereo
    
    Args:
        audio: Mono audio data
        channel_diff: Amplitude difference between channels
        
    Returns:
        Stereo audio (samples x 2)
    """
    left = audio
    right = audio * (1.0 - channel_diff)
    return np.stack([left, right], axis=1)


def measure_silence(
    audio: np.ndarray,
    sample_rate: int,
    threshold: float = -42.0
) -> Tuple[float, float]:
    """
    Measure silence duration at start and end
    
    Args:
        audio: Audio data
        sample_rate: Sample rate in Hz
        threshold: dB threshold for silence detection
        
    Returns:
        Tuple of (leading_silence_duration, trailing_silence_duration) in seconds
    """
    # Convert to dB
    audio_db = 20 * np.log10(np.abs(audio) + 1e-10)
    
    # Find first non-silent sample
    leading_samples = 0
    for i, db_val in enumerate(audio_db):
        if db_val > threshold:
            leading_samples = i
            break
    
    # Find last non-silent sample
    trailing_samples = 0
    for i, db_val in enumerate(reversed(audio_db)):
        if db_val > threshold:
            trailing_samples = i
            break
    
    leading_duration = leading_samples / sample_rate
    trailing_duration = trailing_samples / sample_rate
    
    return leading_duration, trailing_duration


def compare_audio_similarity(
    audio1: np.ndarray,
    audio2: np.ndarray,
    sample_rate: int
) -> float:
    """
    Compare audio similarity using correlation
    
    Args:
        audio1: First audio
        audio2: Second audio
        sample_rate: Sample rate
        
    Returns:
        Similarity score (0.0-1.0, higher is more similar)
    """
    # Ensure same length
    min_len = min(len(audio1), len(audio2))
    audio1 = audio1[:min_len]
    audio2 = audio2[:min_len]
    
    # Normalize
    audio1 = audio1 / (np.max(np.abs(audio1)) + 1e-10)
    audio2 = audio2 / (np.max(np.abs(audio2)) + 1e-10)
    
    # Compute correlation
    correlation = np.corrcoef(audio1, audio2)[0, 1]
    
    return abs(correlation)


def save_test_audio(
    audio: np.ndarray,
    sample_rate: int,
    filepath: str
):
    """
    Save test audio to file
    
    Args:
        audio: Audio data
        sample_rate: Sample rate
        filepath: Output file path
    """
    sf.write(filepath, audio, sample_rate)


def get_audio_duration(audio: np.ndarray, sample_rate: int) -> float:
    """Get audio duration in seconds"""
    return len(audio) / sample_rate
