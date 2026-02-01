export const CONFIG = {
  baseUrl: typeof window !== 'undefined' ? window.location.origin : '',
  endpoints: {
    health: '/health',
    modelsHealth: '/health/models',
    customVoice: {
      generate: '/api/v1/custom-voice/generate',
      speakers: '/api/v1/custom-voice/speakers',
      languages: '/api/v1/custom-voice/languages',
    },
    voiceDesign: {
      generate: '/api/v1/voice-design/generate',
    },
    base: {
      clone: '/api/v1/base/clone',
      createPrompt: '/api/v1/base/create-prompt',
      generateWithPrompt: '/api/v1/base/generate-with-prompt',
      uploadRefAudio: '/api/v1/base/upload-ref-audio',
      cacheStats: '/api/v1/base/cache/stats',
      cacheClear: '/api/v1/base/cache/clear',
    },
  },
};
