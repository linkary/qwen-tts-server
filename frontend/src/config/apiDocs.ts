export interface ApiEndpoint {
  method: string;
  path: string;
}

export interface ApiDocSubTab {
  id: string;
  label: string;
  title: string;
  description: string;
  endpoint: ApiEndpoint;
  docsAnchor?: string;
  requestHeaders?: Array<{ name: string; value: string; description: string }>;
  requestParams?: Array<{ name: string; type: string; required: boolean; description: string }>;
  requestExample?: any;
  responseExample?: any;
  responseHeaders?: Array<{ name: string; description: string }>;
  curlExample?: string;
}

export interface ApiDocSection {
  title: string;
  description: string;
  endpoint?: ApiEndpoint;
  docsAnchor?: string;
  requestHeaders?: Array<{ name: string; value: string; description: string }>;
  requestParams?: Array<{ name: string; type: string; required: boolean; description: string }>;
  requestExample?: any;
  responseExample?: any;
  responseHeaders?: Array<{ name: string; description: string }>;
  curlExample?: string;
  subTabs?: ApiDocSubTab[];
  additionalEndpoints?: Array<{
    title: string;
    endpoint: ApiEndpoint;
    docsAnchor?: string;
    requestHeaders?: Array<{ name: string; value: string; description: string }>;
    requestParams?: Array<{ name: string; type: string; required: boolean; description: string }>;
    requestExample?: any;
    responseExample?: any;
    description?: string;
    curlExample?: string;
  }>;
}

export const API_DOCS: Record<string, ApiDocSection> = {
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
