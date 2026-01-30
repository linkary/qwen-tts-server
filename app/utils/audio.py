"""
Audio processing utilities
"""
import io
import base64
import tempfile
import logging
from typing import Tuple, Union, Optional, Dict, Any
import numpy as np
import soundfile as sf
import aiofiles
import httpx

logger = logging.getLogger(__name__)


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


class AudioValidationError(Exception):
    """Exception raised for audio validation errors"""
    pass


def validate_audio_file(
    file_content: bytes,
    filename: str,
    max_size_mb: float = 5.0,
    max_duration: float = 60.0,
    allowed_formats: set = {'wav', 'mp3', 'flac', 'ogg', 'm4a', 'opus'}
) -> Tuple[np.ndarray, int, Dict[str, Any]]:
    """
    Validate audio file with multiple checks
    
    Args:
        file_content: Audio file content as bytes
        filename: Original filename
        max_size_mb: Maximum file size in MB
        max_duration: Maximum audio duration in seconds
        allowed_formats: Set of allowed file extensions
        
    Returns:
        Tuple of (audio_data, sample_rate, metadata)
        
    Raises:
        AudioValidationError: If validation fails
    """
    from app.config import settings
    
    # Check file size
    size_mb = len(file_content) / (1024 * 1024)
    if size_mb > max_size_mb:
        raise AudioValidationError(
            f"File size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
        )
    
    # Check file extension
    file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
    if file_ext not in allowed_formats:
        raise AudioValidationError(
            f"File extension '.{file_ext}' not allowed. Allowed formats: {', '.join(allowed_formats)}"
        )
    
    # Validate MIME type using python-magic if available
    try:
        import magic
        mime_type = magic.from_buffer(file_content, mime=True)
        if not mime_type.startswith('audio/'):
            raise AudioValidationError(
                f"Invalid file content. Detected MIME type: {mime_type}"
            )
    except ImportError:
        logger.warning("python-magic not available, skipping MIME type validation")
    except Exception as e:
        logger.warning(f"MIME type validation failed: {e}")
    
    # Try to load audio
    try:
        audio_data, sample_rate = sf.read(io.BytesIO(file_content))
    except Exception as e:
        raise AudioValidationError(f"Failed to read audio file: {str(e)}")
    
    # Check duration
    duration = len(audio_data) / sample_rate
    if duration > max_duration:
        raise AudioValidationError(
            f"Audio duration ({duration:.2f}s) exceeds maximum allowed duration ({max_duration}s)"
        )
    
    metadata = {
        "size_mb": size_mb,
        "duration": duration,
        "sample_rate": sample_rate,
        "channels": audio_data.ndim,
        "format": file_ext
    }
    
    logger.debug(f"Audio validation passed: {metadata}")
    return audio_data, sample_rate, metadata


def preprocess_reference_audio(
    audio_data: np.ndarray,
    sample_rate: int,
    max_duration: float = 15.0,
    target_duration_min: float = 5.0,
) -> Tuple[np.ndarray, int, Dict[str, Any]]:
    """
    Preprocess reference audio with smart clipping and silence removal
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate in Hz
        max_duration: Maximum duration in seconds
        target_duration_min: Minimum target duration in seconds
        
    Returns:
        Tuple of (processed_audio, sample_rate, metadata)
    """
    from app.config import settings
    
    original_duration = len(audio_data) / sample_rate
    metadata = {
        "original_duration": original_duration,
        "sample_rate": sample_rate,
    }
    
    # Convert to mono if stereo
    if audio_data.ndim > 1:
        audio_data = np.mean(audio_data, axis=1)
        metadata["converted_to_mono"] = True
    
    try:
        from pydub import AudioSegment, silence
        import io
        
        # Convert to AudioSegment for processing
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV')
        buffer.seek(0)
        aseg = AudioSegment.from_wav(buffer)
        
        # Smart clipping if audio is too long
        if len(aseg) > max_duration * 1000:
            logger.debug(f"Audio duration {len(aseg)/1000:.2f}s exceeds max {max_duration}s, clipping...")
            
            # Try to find long silence for clipping
            non_silent_segs = silence.split_on_silence(
                aseg,
                min_silence_len=1000,
                silence_thresh=-50,
                keep_silence=1000,
                seek_step=10
            )
            
            non_silent_wave = AudioSegment.silent(duration=0)
            for seg in non_silent_segs:
                if (len(non_silent_wave) > target_duration_min * 1000 and 
                    len(non_silent_wave + seg) > max_duration * 1000):
                    logger.debug("Clipped at long silence boundary")
                    metadata["clip_method"] = "long_silence"
                    break
                non_silent_wave += seg
            
            # If still too long, try short silence
            if len(non_silent_wave) > max_duration * 1000:
                non_silent_segs = silence.split_on_silence(
                    aseg,
                    min_silence_len=100,
                    silence_thresh=-40,
                    keep_silence=1000,
                    seek_step=10
                )
                
                non_silent_wave = AudioSegment.silent(duration=0)
                for seg in non_silent_segs:
                    if (len(non_silent_wave) > target_duration_min * 1000 and 
                        len(non_silent_wave + seg) > max_duration * 1000):
                        logger.debug("Clipped at short silence boundary")
                        metadata["clip_method"] = "short_silence"
                        break
                    non_silent_wave += seg
            
            # Hard clip if still too long
            if len(non_silent_wave) > max_duration * 1000:
                non_silent_wave = aseg[:int(max_duration * 1000)]
                logger.debug("Hard clipped to max duration")
                metadata["clip_method"] = "hard_clip"
            
            aseg = non_silent_wave
        
        # Remove leading/trailing silence
        def detect_leading_silence(audio_seg, silence_threshold=-42, chunk_size=10):
            trim_ms = 0
            while (trim_ms < len(audio_seg) and 
                   audio_seg[trim_ms:trim_ms + chunk_size].dBFS < silence_threshold):
                trim_ms += chunk_size
            return trim_ms
        
        start_trim = detect_leading_silence(aseg)
        end_trim = detect_leading_silence(aseg.reverse())
        duration_ms = len(aseg)
        
        if start_trim > 0 or end_trim > 0:
            aseg = aseg[start_trim:duration_ms - end_trim]
            metadata["silence_removed_ms"] = start_trim + end_trim
            logger.debug(f"Removed {start_trim}ms leading and {end_trim}ms trailing silence")
        
        # Add small tail for natural ending
        aseg = aseg + AudioSegment.silent(duration=50)
        
        # Convert back to numpy
        buffer = io.BytesIO()
        aseg.export(buffer, format='wav')
        buffer.seek(0)
        audio_data, sample_rate = sf.read(buffer)
        
        metadata["processed_duration"] = len(audio_data) / sample_rate
        logger.debug(f"Preprocessing complete: {original_duration:.2f}s -> {metadata['processed_duration']:.2f}s")
        
    except ImportError:
        logger.warning("pydub not available, skipping advanced preprocessing")
        # Basic preprocessing: just clip to max duration
        max_samples = int(max_duration * sample_rate)
        if len(audio_data) > max_samples:
            audio_data = audio_data[:max_samples]
            metadata["clip_method"] = "basic_clip"
            metadata["processed_duration"] = max_duration
    
    return audio_data, sample_rate, metadata


def apply_speed(audio_data: np.ndarray, sample_rate: int, speed: float) -> np.ndarray:
    """
    Apply speed adjustment to audio using time stretching
    
    Args:
        audio_data: Audio data as numpy array
        sample_rate: Sample rate in Hz
        speed: Speed multiplier (>1 = faster, <1 = slower)
        
    Returns:
        Speed-adjusted audio data
    """
    if speed == 1.0:
        return audio_data
    
    try:
        import librosa
        # Time stretch: speed > 1 = faster, speed < 1 = slower
        return librosa.effects.time_stretch(audio_data, rate=speed)
    except ImportError:
        logger.warning("librosa not installed, speed adjustment not available")
        return audio_data
    except Exception as e:
        logger.error(f"Failed to apply speed adjustment: {e}")
        return audio_data


async def prepare_ref_audio(
    ref_audio_url: Optional[str] = None,
    ref_audio_base64: Optional[str] = None,
    ref_audio_file: Optional[bytes] = None,
    preprocess: bool = True,
    validate: bool = True,
) -> Optional[Tuple[np.ndarray, int]]:
    """
    Prepare reference audio from various sources with optional preprocessing
    
    Args:
        ref_audio_url: URL to reference audio
        ref_audio_base64: Base64 encoded reference audio
        ref_audio_file: Raw file bytes
        preprocess: Whether to apply preprocessing
        validate: Whether to validate audio (only for file uploads)
        
    Returns:
        Tuple of (audio_data, sample_rate) or None
    """
    from app.config import settings
    
    # Load audio from source
    if ref_audio_url:
        audio_data, sample_rate = await load_audio_from_url(ref_audio_url)
    elif ref_audio_base64:
        audio_data, sample_rate = load_audio_from_base64(ref_audio_base64)
    elif ref_audio_file:
        # Validate if enabled
        if validate and settings.audio_upload_max_size_mb > 0:
            audio_data, sample_rate, _ = validate_audio_file(
                ref_audio_file,
                "uploaded_audio",
                max_size_mb=settings.audio_upload_max_size_mb,
                max_duration=settings.audio_upload_max_duration
            )
        else:
            audio_data, sample_rate = await load_audio_from_file(ref_audio_file)
    else:
        return None
    
    # Apply preprocessing if enabled
    if preprocess and settings.audio_preprocessing_enabled:
        audio_data, sample_rate, metadata = preprocess_reference_audio(
            audio_data,
            sample_rate,
            max_duration=settings.ref_audio_max_duration,
            target_duration_min=settings.ref_audio_target_duration_min
        )
        logger.debug(f"Reference audio preprocessed: {metadata}")
    
    return audio_data, sample_rate
