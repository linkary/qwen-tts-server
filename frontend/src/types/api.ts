export interface GenerateCustomVoiceRequest {
  text: string;
  language: string;
  speaker: string;
  instruct?: string;
  speed?: number;
  response_format?: 'base64' | 'float';
}

export interface GenerateVoiceDesignRequest {
  text: string;
  language: string;
  instruct: string;
  speed?: number;
  response_format?: 'base64' | 'float';
}

export interface CloneVoiceRequest {
  text: string;
  language: string;
  ref_audio_base64: string;
  ref_text?: string;
  x_vector_only_mode?: boolean;
  speed?: number;
  response_format?: 'base64' | 'float';
}

export interface CreatePromptRequest {
  ref_audio_base64: string;
  ref_text?: string;
  x_vector_only_mode?: boolean;
}

export interface GenerateWithPromptRequest {
  text: string;
  language: string;
  prompt_id: string;
  speed?: number;
  response_format?: 'base64' | 'float';
}

export interface AudioResponse {
  audio: string; // base64 encoded
  sample_rate: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface ModelsHealthResponse {
  custom_voice_loaded: boolean;
  voice_design_loaded: boolean;
  base_loaded: boolean;
}

export interface CacheStatsResponse {
  enabled: boolean;
  size: number;
  max_size: number;
  hits: number;
  misses: number;
  evictions: number;
  hit_rate_percent: number;
  total_requests: number;
}

export interface CreatePromptResponse {
  prompt_id: string;
  message: string;
}

export interface UploadRefAudioResponse {
  filename: string;
  content_type: string;
  audio_base64: string;
  message: string;
}

export interface ApiErrorResponse {
  detail: string;
}
