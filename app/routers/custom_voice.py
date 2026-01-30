"""
CustomVoice API endpoints
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from app.auth import verify_api_key
from app.models.schemas import (
    CustomVoiceRequest,
    CustomVoiceBatchRequest,
    AudioResponse,
    BatchAudioResponse,
    SpeakersResponse,
    SpeakerInfo,
    LanguagesResponse,
)
from app.models.manager import model_manager
from app.utils.audio import numpy_to_wav_bytes, numpy_to_base64
from app.utils.streaming import stream_audio_base64_chunks, create_sse_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/custom-voice", tags=["custom-voice"])


# Speaker information
SPEAKERS = [
    SpeakerInfo(
        name="Vivian",
        description="Bright, slightly edgy young female voice",
        native_language="Chinese"
    ),
    SpeakerInfo(
        name="Serena",
        description="Warm, gentle young female voice",
        native_language="Chinese"
    ),
    SpeakerInfo(
        name="Uncle_Fu",
        description="Seasoned male voice with a low, mellow timbre",
        native_language="Chinese"
    ),
    SpeakerInfo(
        name="Dylan",
        description="Youthful Beijing male voice with a clear, natural timbre",
        native_language="Chinese (Beijing Dialect)"
    ),
    SpeakerInfo(
        name="Eric",
        description="Lively Chengdu male voice with a slightly husky brightness",
        native_language="Chinese (Sichuan Dialect)"
    ),
    SpeakerInfo(
        name="Ryan",
        description="Dynamic male voice with strong rhythmic drive",
        native_language="English"
    ),
    SpeakerInfo(
        name="Aiden",
        description="Sunny American male voice with a clear midrange",
        native_language="English"
    ),
    SpeakerInfo(
        name="Ono_Anna",
        description="Playful Japanese female voice with a light, nimble timbre",
        native_language="Japanese"
    ),
    SpeakerInfo(
        name="Sohee",
        description="Warm Korean female voice with rich emotion",
        native_language="Korean"
    ),
]


SUPPORTED_LANGUAGES = [
    "Auto",
    "Chinese",
    "English",
    "Japanese",
    "Korean",
    "German",
    "French",
    "Russian",
    "Portuguese",
    "Spanish",
    "Italian"
]


@router.post("/generate")
async def generate_custom_voice(
    request: CustomVoiceRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate speech using CustomVoice model with preset speakers
    
    Returns audio file (WAV) or base64 encoded audio based on response_format
    """
    try:
        logger.info(f"Generating custom voice for speaker: {request.speaker}")
        
        # Get model
        model = model_manager.get_custom_voice_model()
        
        # Generate audio
        wavs, sr = model.generate_custom_voice(
            text=request.text,
            language=request.language,
            speaker=request.speaker,
            instruct=request.instruct if request.instruct else "",
        )
        
        # Return based on format
        if request.response_format == "base64":
            audio_base64 = numpy_to_base64(wavs[0], sr)
            return AudioResponse(
                audio=audio_base64,
                sample_rate=sr,
                format="wav"
            )
        else:
            # Return WAV file
            wav_bytes = numpy_to_wav_bytes(wavs[0], sr)
            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": f"attachment; filename=custom_voice_{request.speaker}.wav"
                }
            )
    
    except Exception as e:
        logger.error(f"Error generating custom voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-stream")
async def generate_custom_voice_stream(
    request: CustomVoiceRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate speech using CustomVoice model with streaming output
    
    Returns Server-Sent Events with audio chunks
    """
    try:
        logger.info(f"Generating custom voice stream for speaker: {request.speaker}")
        
        # Get model
        model = model_manager.get_custom_voice_model()
        
        # Generate audio
        wavs, sr = model.generate_custom_voice(
            text=request.text,
            language=request.language,
            speaker=request.speaker,
            instruct=request.instruct if request.instruct else "",
        )
        
        # Stream audio chunks
        async def generate():
            yield create_sse_message(f'{{"sample_rate": {sr}}}', "metadata")
            
            async for chunk_base64 in stream_audio_base64_chunks(wavs[0], sr):
                yield create_sse_message(chunk_base64, "audio")
            
            yield create_sse_message("complete", "done")
        
        return EventSourceResponse(generate())
    
    except Exception as e:
        logger.error(f"Error generating custom voice stream: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch")
async def generate_custom_voice_batch(
    request: CustomVoiceBatchRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate multiple speech samples using CustomVoice model
    
    Returns base64 encoded audio array
    """
    try:
        logger.info(f"Batch generating {len(request.texts)} custom voice samples")
        
        # Validate input lengths
        if len(request.texts) != len(request.languages) or len(request.texts) != len(request.speakers):
            raise HTTPException(
                status_code=400,
                detail="texts, languages, and speakers must have the same length"
            )
        
        if request.instructs and len(request.instructs) != len(request.texts):
            raise HTTPException(
                status_code=400,
                detail="instructs must have the same length as texts"
            )
        
        # Get model
        model = model_manager.get_custom_voice_model()
        
        # Prepare instructs
        instructs = request.instructs if request.instructs else [""] * len(request.texts)
        
        # Generate audio
        wavs, sr = model.generate_custom_voice(
            text=request.texts,
            language=request.languages,
            speaker=request.speakers,
            instruct=instructs,
        )
        
        # Convert to base64
        audio_base64_list = [numpy_to_base64(wav, sr) for wav in wavs]
        
        return BatchAudioResponse(
            audios=audio_base64_list,
            sample_rate=sr,
            format="wav"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating custom voice batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/speakers", response_model=SpeakersResponse)
async def list_speakers(api_key: str = Depends(verify_api_key)):
    """
    List available speakers for CustomVoice model
    """
    return SpeakersResponse(speakers=SPEAKERS)


@router.get("/languages", response_model=LanguagesResponse)
async def list_languages(api_key: str = Depends(verify_api_key)):
    """
    List supported languages for CustomVoice model
    """
    return LanguagesResponse(languages=SUPPORTED_LANGUAGES)
