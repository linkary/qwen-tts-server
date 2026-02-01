import { CONFIG } from '../config/api';
import type {
  GenerateCustomVoiceRequest,
  GenerateVoiceDesignRequest,
  CloneVoiceRequest,
  CreatePromptRequest,
  GenerateWithPromptRequest,
  AudioResponse,
  HealthResponse,
  ModelsHealthResponse,
  CacheStatsResponse,
  CreatePromptResponse,
  UploadRefAudioResponse,
  ApiErrorResponse,
} from '../types/api';

/**
 * Get headers with API key
 */
export function getHeaders(apiKey?: string, contentType: string = 'application/json'): HeadersInit {
  const headers: HeadersInit = {};
  if (contentType) {
    headers['Content-Type'] = contentType;
  }
  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }
  return headers;
}

/**
 * Handle API errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiErrorResponse = await response.json();
    throw new Error(error.detail || 'API request failed');
  }
  return response.json();
}

/**
 * Check server health
 */
export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.health}`);
  return handleResponse<HealthResponse>(response);
}

/**
 * Check models health
 */
export async function checkModelsHealth(): Promise<ModelsHealthResponse> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.modelsHealth}`);
  return handleResponse<ModelsHealthResponse>(response);
}

/**
 * Fetch cache statistics
 */
export async function fetchCacheStats(apiKey: string): Promise<CacheStatsResponse> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.base.cacheStats}`, {
    headers: getHeaders(apiKey, ''),
  });
  return handleResponse<CacheStatsResponse>(response);
}

/**
 * Clear cache
 */
export async function clearCache(apiKey: string): Promise<void> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.base.cacheClear}`, {
    method: 'POST',
    headers: getHeaders(apiKey, ''),
  });
  if (!response.ok) {
    throw new Error('Failed to clear cache');
  }
}

/**
 * Generate custom voice speech
 */
export async function generateCustomVoice(
  request: GenerateCustomVoiceRequest,
  apiKey: string
): Promise<{ data: AudioResponse; headers: Headers }> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.customVoice.generate}`, {
    method: 'POST',
    headers: getHeaders(apiKey),
    body: JSON.stringify({
      ...request,
      response_format: request.response_format || 'base64',
    }),
  });
  
  const data = await handleResponse<AudioResponse>(response);
  return { data, headers: response.headers };
}

/**
 * Generate voice design speech
 */
export async function generateVoiceDesign(
  request: GenerateVoiceDesignRequest,
  apiKey: string
): Promise<{ data: AudioResponse; headers: Headers }> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.voiceDesign.generate}`, {
    method: 'POST',
    headers: getHeaders(apiKey),
    body: JSON.stringify({
      ...request,
      response_format: request.response_format || 'base64',
    }),
  });
  
  const data = await handleResponse<AudioResponse>(response);
  return { data, headers: response.headers };
}

/**
 * Clone voice
 */
export async function cloneVoice(
  request: CloneVoiceRequest,
  apiKey: string
): Promise<{ data: AudioResponse; headers: Headers }> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.base.clone}`, {
    method: 'POST',
    headers: getHeaders(apiKey),
    body: JSON.stringify({
      ...request,
      response_format: request.response_format || 'base64',
    }),
  });
  
  const data = await handleResponse<AudioResponse>(response);
  return { data, headers: response.headers };
}

/**
 * Create voice prompt
 */
export async function createVoicePrompt(
  request: CreatePromptRequest,
  apiKey: string
): Promise<CreatePromptResponse> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.base.createPrompt}`, {
    method: 'POST',
    headers: getHeaders(apiKey),
    body: JSON.stringify(request),
  });
  
  return handleResponse<CreatePromptResponse>(response);
}

/**
 * Generate with saved prompt
 */
export async function generateWithPrompt(
  request: GenerateWithPromptRequest,
  apiKey: string
): Promise<{ data: AudioResponse; headers: Headers }> {
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.base.generateWithPrompt}`, {
    method: 'POST',
    headers: getHeaders(apiKey),
    body: JSON.stringify({
      ...request,
      response_format: request.response_format || 'base64',
    }),
  });
  
  const data = await handleResponse<AudioResponse>(response);
  return { data, headers: response.headers };
}

/**
 * Upload reference audio
 */
export async function uploadRefAudio(
  file: File,
  apiKey: string
): Promise<UploadRefAudioResponse> {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${CONFIG.baseUrl}${CONFIG.endpoints.base.uploadRefAudio}`, {
    method: 'POST',
    headers: getHeaders(apiKey, ''), // No content-type for FormData
    body: formData,
  });
  
  return handleResponse<UploadRefAudioResponse>(response);
}
