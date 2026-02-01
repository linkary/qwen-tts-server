/**
 * API Documentation Configuration
 * Ported from static demo for API documentation panel
 */

export interface ApiEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
}

export interface ApiHeader {
  name: string;
  value?: string;
  description: string;
}

export interface ApiParam {
  name: string;
  type: string;
  required: boolean;
  description: string;
}

export interface ApiSubTab {
  id: string;
  label: string;
  title: string;
  description: string;
  endpoint: ApiEndpoint;
  docsAnchor?: string;
  requestHeaders?: ApiHeader[];
  requestParams?: ApiParam[];
  requestExample?: Record<string, any>;
  responseExample?: Record<string, any>;
  responseHeaders?: ApiHeader[];
  curlExample?: string;
}

export interface ApiAdditionalEndpoint {
  title: string;
  endpoint: ApiEndpoint;
  description?: string;
  responseExample?: Record<string, any>;
}

export interface ApiDocConfig {
  title: string;
  description: string;
  endpoint?: ApiEndpoint;
  docsAnchor?: string;
  requestHeaders?: ApiHeader[];
  requestParams?: ApiParam[];
  requestExample?: Record<string, any> | null;
  responseExample?: Record<string, any>;
  responseHeaders?: ApiHeader[];
  curlExample?: string;
  subTabs?: ApiSubTab[];
  additionalEndpoints?: ApiAdditionalEndpoint[];
}

export type ApiDocsMap = {
  'custom-voice': ApiDocConfig;
  'voice-design': ApiDocConfig;
  'voice-clone': ApiDocConfig;
  'settings': ApiDocConfig;
};

export const API_DOCS: ApiDocsMap = {
  'custom-voice': {
    title: 'Custom Voice API',
    description: 'Generate speech using one of 9 preset speakers. Supports emotional control via style instructions and multiple languages.',
    endpoint: {
      method: 'POST',
      path: '/api/v1/custom-voice/generate'
    },
    docsAnchor: '#/custom-voice/generate_custom_voice_api_v1_custom_voice_generate_post',
    requestHeaders: [
      { name: 'Content-Type', value: 'application/json', description: 'Request body format' },
      { name: 'X-API-Key', value: 'your-api-key', description: 'API authentication key' }
    ],
    requestParams: [
      { name: 'text', type: 'string', required: true, description: 'Text to synthesize' },
      { name: 'speaker', type: 'string', required: true, description: 'Name of the speaker' },
      { name: 'language', type: 'string', required: false, description: 'Language code or "Auto"' },
      { name: 'instruct', type: 'string', required: false, description: 'Style/emotion instruction' },
      { name: 'speed', type: 'number', required: false, description: 'Speech speed (0.5 to 2.0)' },
      { name: 'response_format', type: 'string', required: false, description: 'Audio format ("base64" or "float")' }
    ],
    requestExample: {
      text: 'Hello, welcome to the Qwen3-TTS demo!',
      language: 'English',
      speaker: 'Ryan',
      instruct: 'Speak cheerfully with energy',
      speed: 1.0,
      response_format: 'base64'
    },
    responseExample: {
      audio: '<base64_encoded_audio_data>',
      sample_rate: 24000
    },
    responseHeaders: [
      { name: 'X-Audio-Duration', description: 'Duration of generated audio in seconds' },
      { name: 'X-RTF', description: 'Real-time factor (generation_time / audio_duration)' },
      { name: 'X-Generation-Time', description: 'Time taken to generate audio in seconds' }
    ],
    curlExample: `curl -X POST "{{baseUrl}}/api/v1/custom-voice/generate" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{
    "text": "Hello, welcome to the demo!",
    "language": "English",
    "speaker": "Ryan",
    "instruct": "Speak cheerfully",
    "speed": 1.0,
    "response_format": "base64"
  }'`
  },
  'voice-design': {
    title: 'Voice Design API',
    description: 'Create custom voices using natural language descriptions. Describe the voice characteristics you want (age, gender, accent, emotion, etc.).',
    endpoint: {
      method: 'POST',
      path: '/api/v1/voice-design/generate'
    },
    docsAnchor: '#/voice-design/generate_voice_design_api_v1_voice_design_generate_post',
    requestHeaders: [
      { name: 'Content-Type', value: 'application/json', description: 'Request body format' },
      { name: 'X-API-Key', value: 'your-api-key', description: 'API authentication key' }
    ],
    requestParams: [
      { name: 'text', type: 'string', required: true, description: 'Text to synthesize' },
      { name: 'instruct', type: 'string', required: true, description: 'Voice description prompt' },
      { name: 'language', type: 'string', required: false, description: 'Language code or "Auto"' },
      { name: 'speed', type: 'number', required: false, description: 'Speech speed (0.5 to 2.0)' },
      { name: 'response_format', type: 'string', required: false, description: 'Audio format ("base64" or "float")' }
    ],
    requestExample: {
      text: 'Welcome to the future of voice synthesis.',
      language: 'English',
      instruct: 'A warm, professional female voice with a slight British accent, speaking confidently and clearly',
      speed: 1.0,
      response_format: 'base64'
    },
    responseExample: {
      audio: '<base64_encoded_audio_data>',
      sample_rate: 24000
    },
    responseHeaders: [
      { name: 'X-Audio-Duration', description: 'Duration of generated audio in seconds' },
      { name: 'X-RTF', description: 'Real-time factor (generation_time / audio_duration)' },
      { name: 'X-Generation-Time', description: 'Time taken to generate audio in seconds' }
    ],
    curlExample: `curl -X POST "{{baseUrl}}/api/v1/voice-design/generate" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{
    "text": "Welcome to the future of voice synthesis.",
    "language": "English",
    "instruct": "A warm, professional female voice with clear enunciation",
    "speed": 1.0,
    "response_format": "base64"
  }'`
  },
  'voice-clone': {
    title: 'Voice Clone API',
    description: 'Clone any voice from a reference audio sample. Choose a method below:',
    subTabs: [
      {
        id: 'vc-clone',
        label: 'Clone (Base)',
        title: 'Voice Clone API',
        description: 'Clone any voice from a reference audio sample. Provide the audio and transcript to generate new speech in that voice.',
        endpoint: {
          method: 'POST',
          path: '/api/v1/base/clone'
        },
        docsAnchor: '#/base/clone_voice_api_v1_base_clone_post',
        requestHeaders: [
          { name: 'Content-Type', value: 'application/json', description: 'Request body format' },
          { name: 'X-API-Key', value: 'your-api-key', description: 'API authentication key' }
        ],
        requestParams: [
          { name: 'text', type: 'string', required: true, description: 'Text to synthesize' },
          { name: 'ref_audio_base64', type: 'string', required: true, description: 'Reference audio (base64 encoded)' },
          { name: 'ref_text', type: 'string', required: false, description: 'Transcript of reference audio (required if x_vector_only_mode is false)' },
          { name: 'language', type: 'string', required: false, description: 'Language code or "Auto"' },
          { name: 'x_vector_only_mode', type: 'boolean', required: false, description: 'Use X-vector only (no transcript)' },
          { name: 'speed', type: 'number', required: false, description: 'Speech speed (0.5 to 2.0)' },
          { name: 'response_format', type: 'string', required: false, description: 'Audio format' }
        ],
        requestExample: {
          text: 'This is my cloned voice speaking new words.',
          language: 'English',
          ref_audio_base64: '<base64_encoded_reference_audio>',
          ref_text: 'The original text spoken in the reference audio.',
          x_vector_only_mode: false,
          speed: 1.0,
          response_format: 'base64'
        },
        responseExample: {
          audio: '<base64_encoded_audio_data>',
          sample_rate: 24000
        },
        responseHeaders: [
          { name: 'X-Audio-Duration', description: 'Duration of generated audio in seconds' },
          { name: 'X-RTF', description: 'Real-time factor (generation_time / audio_duration)' },
          { name: 'X-Cache-Status', description: 'Whether the prompt was cached (HIT/MISS)' }
        ],
        curlExample: `curl -X POST "{{baseUrl}}/api/v1/base/clone" \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your-api-key" \\
  -d '{
    "text": "This is my cloned voice.",
    "language": "English",
    "ref_audio_base64": "<base64_audio>",
    "ref_text": "Reference text here",
    "x_vector_only_mode": false,
    "speed": 1.0,
    "response_format": "base64"
  }'`
      },
      {
        id: 'vc-upload',
        label: 'Upload Audio',
        title: 'Upload Reference Audio',
        description: 'Upload an audio file to get its base64 string. Use this if you want to use a file instead of raw base64.',
        endpoint: { method: 'POST', path: '/api/v1/base/upload-ref-audio' },
        docsAnchor: '#/base/upload_reference_audio_api_v1_base_upload_ref_audio_post',
        requestHeaders: [
          { name: 'Content-Type', value: 'multipart/form-data', description: 'File upload' },
          { name: 'X-API-Key', value: 'your-api-key', description: 'API authentication key' }
        ],
        requestParams: [
          { name: 'file', type: 'file', required: true, description: 'Audio file to upload (WAV, MP3, etc.)' }
        ],
        responseExample: {
          filename: 'my_voice.wav',
          content_type: 'audio/wav',
          audio_base64: '<base64_encoded_string>',
          message: 'File uploaded and encoded successfully'
        },
        curlExample: `curl -X POST "{{baseUrl}}/api/v1/base/upload-ref-audio" \\
  -H "X-API-Key: your-api-key" \\
  -F "file=@/path/to/your/audio.wav"`
      },
      {
        id: 'vc-create-prompt',
        label: 'Create Prompt',
        title: 'Create Reusable Prompt',
        description: 'Create a cached prompt from reference audio for faster subsequent generations.',
        endpoint: { method: 'POST', path: '/api/v1/base/create-prompt' },
        requestExample: {
          ref_audio_base64: '<base64_encoded_reference_audio>',
          ref_text: 'The original text spoken in the reference audio.',
          x_vector_only_mode: false
        },
        responseExample: {
          prompt_id: 'abc123-def456-ghi789'
        }
      },
      {
        id: 'vc-gen-prompt',
        label: 'Use Prompt',
        title: 'Generate with Saved Prompt',
        description: 'Generate speech using a previously saved voice prompt.',
        endpoint: { method: 'POST', path: '/api/v1/base/generate-with-prompt' },
        requestExample: {
          text: 'Text to synthesize with the saved voice.',
          language: 'English',
          prompt_id: 'abc123-def456-ghi789',
          response_format: 'base64'
        }
      }
    ]
  },
  'settings': {
    title: 'Health & Cache APIs',
    description: 'Monitor server health, model status, and manage the voice prompt cache.',
    endpoint: {
      method: 'GET',
      path: '/health'
    },
    requestExample: null,
    responseExample: {
      status: 'healthy',
      version: '1.0.0',
      timestamp: '2024-01-01T00:00:00Z'
    },
    additionalEndpoints: [
      {
        title: 'Models Health',
        endpoint: { method: 'GET', path: '/health/models' },
        responseExample: {
          custom_voice_loaded: true,
          voice_design_loaded: true,
          base_loaded: true
        }
      },
      {
        title: 'Cache Statistics',
        endpoint: { method: 'GET', path: '/api/v1/base/cache/stats' },
        responseExample: {
          enabled: true,
          size: 5,
          max_size: 100,
          hit_rate_percent: 75.5,
          total_requests: 120
        }
      },
      {
        title: 'Clear Cache',
        endpoint: { method: 'POST', path: '/api/v1/base/cache/clear' },
        responseExample: {
          message: 'Cache cleared successfully'
        }
      }
    ],
    curlExample: `# Check server health
curl "{{baseUrl}}/health"

# Check models status
curl "{{baseUrl}}/health/models"

# Get cache statistics
curl "{{baseUrl}}/api/v1/base/cache/stats" \\
  -H "X-API-Key: your-api-key"

# Clear cache
curl -X POST "{{baseUrl}}/api/v1/base/cache/clear" \\
  -H "X-API-Key: your-api-key"`
  }
};
