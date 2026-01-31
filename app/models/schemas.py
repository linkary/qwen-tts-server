"""
Pydantic models for request and response schemas
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error_type: Optional[str] = None


class CustomVoiceRequest(BaseModel):
    """Request schema for CustomVoice generation"""
    text: str = Field(..., description="Text to synthesize", min_length=1)
    language: str = Field(
        default="Auto",
        description="Language code (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian, or Auto)"
    )
    speaker: str = Field(..., description="Speaker name (e.g., Vivian, Serena, Ryan)")
    instruct: Optional[str] = Field(
        default=None,
        description="Optional instruction for controlling voice style (e.g., 'Very happy', 'Angry tone')"
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed multiplier (0.5-2.0, default 1.0)"
    )
    response_format: Literal["wav", "base64"] = Field(
        default="wav",
        description="Response format: 'wav' for audio file download, 'base64' for base64 encoded JSON"
    )


class CustomVoiceBatchRequest(BaseModel):
    """Request schema for batch CustomVoice generation"""
    texts: List[str] = Field(..., description="List of texts to synthesize", min_length=1)
    languages: List[str] = Field(..., description="List of language codes matching texts")
    speakers: List[str] = Field(..., description="List of speaker names matching texts")
    instructs: Optional[List[Optional[str]]] = Field(
        default=None,
        description="Optional list of instructions matching texts"
    )
    response_format: Literal["wav", "base64", "zip"] = Field(
        default="zip",
        description="Response format: 'zip' for multiple files, 'base64' for JSON array"
    )


class VoiceDesignRequest(BaseModel):
    """Request schema for VoiceDesign generation"""
    text: str = Field(..., description="Text to synthesize", min_length=1)
    language: str = Field(
        default="Auto",
        description="Language code (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian, or Auto)"
    )
    instruct: str = Field(
        ...,
        description="Voice design instruction describing the target voice characteristics",
        min_length=1
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed multiplier (0.5-2.0, default 1.0)"
    )
    response_format: Literal["wav", "base64"] = Field(
        default="wav",
        description="Response format: 'wav' for audio file download, 'base64' for base64 encoded JSON"
    )


class VoiceDesignBatchRequest(BaseModel):
    """Request schema for batch VoiceDesign generation"""
    texts: List[str] = Field(..., description="List of texts to synthesize", min_length=1)
    languages: List[str] = Field(..., description="List of language codes matching texts")
    instructs: List[str] = Field(..., description="List of voice design instructions matching texts")
    response_format: Literal["wav", "base64", "zip"] = Field(
        default="zip",
        description="Response format: 'zip' for multiple files, 'base64' for JSON array"
    )


class VoiceCloneRequest(BaseModel):
    """Request schema for voice cloning"""
    text: str = Field(..., description="Text to synthesize", min_length=1)
    language: str = Field(
        default="Auto",
        description="Language code (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian, or Auto)"
    )
    ref_text: Optional[str] = Field(
        default=None,
        description="Transcript of the reference audio (required if x_vector_only_mode is False)"
    )
    ref_audio_url: Optional[str] = Field(
        default=None,
        description="URL to reference audio file (mutually exclusive with ref_audio_base64)"
    )
    ref_audio_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded reference audio (mutually exclusive with ref_audio_url)"
    )
    x_vector_only_mode: bool = Field(
        default=False,
        description="If True, only use speaker embedding (ref_text not required, but quality may be reduced)"
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed multiplier (0.5-2.0, default 1.0)"
    )
    response_format: Literal["wav", "base64"] = Field(
        default="wav",
        description="Response format: 'wav' for audio file download, 'base64' for base64 encoded JSON"
    )


class CreatePromptRequest(BaseModel):
    """Request schema for creating reusable voice clone prompt"""
    ref_text: Optional[str] = Field(
        default=None,
        description="Transcript of the reference audio (required if x_vector_only_mode is False)"
    )
    ref_audio_url: Optional[str] = Field(
        default=None,
        description="URL to reference audio file (mutually exclusive with ref_audio_base64)"
    )
    ref_audio_base64: Optional[str] = Field(
        default=None,
        description="Base64 encoded reference audio (mutually exclusive with ref_audio_url)"
    )
    x_vector_only_mode: bool = Field(
        default=False,
        description="If True, only use speaker embedding (ref_text not required)"
    )


class CreatePromptResponse(BaseModel):
    """Response schema for create prompt"""
    prompt_id: str = Field(..., description="Unique identifier for the created prompt")
    message: str = Field(default="Prompt created successfully")


class GenerateWithPromptRequest(BaseModel):
    """Request schema for generating with saved prompt"""
    text: str = Field(..., description="Text to synthesize", min_length=1)
    language: str = Field(
        default="Auto",
        description="Language code (Chinese, English, Japanese, Korean, German, French, Russian, Portuguese, Spanish, Italian, or Auto)"
    )
    prompt_id: str = Field(..., description="ID of the saved voice clone prompt")
    response_format: Literal["wav", "base64"] = Field(
        default="wav",
        description="Response format: 'wav' for audio file download, 'base64' for base64 encoded JSON"
    )


class AudioResponse(BaseModel):
    """Response schema for base64 encoded audio"""
    audio: str = Field(..., description="Base64 encoded audio data")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    format: str = Field(default="wav", description="Audio format")


class BatchAudioResponse(BaseModel):
    """Response schema for batch base64 encoded audio"""
    audios: List[str] = Field(..., description="List of base64 encoded audio data")
    sample_rate: int = Field(..., description="Audio sample rate in Hz")
    format: str = Field(default="wav", description="Audio format")


class SpeakerInfo(BaseModel):
    """Information about a speaker"""
    name: str = Field(..., description="Speaker identifier")
    description: str = Field(..., description="Voice characteristics description")
    native_language: str = Field(..., description="Speaker's native language")


class SpeakersResponse(BaseModel):
    """Response schema for listing speakers"""
    speakers: List[SpeakerInfo]


class LanguagesResponse(BaseModel):
    """Response schema for listing languages"""
    languages: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    version: str


class ModelsHealthResponse(BaseModel):
    """Models health check response"""
    custom_voice_loaded: bool
    voice_design_loaded: bool
    base_loaded: bool
    tokenizer_loaded: bool
