/**
 * Qwen3-TTS Demo Application
 * Retro-Futuristic Audio Lab Interface
 */

// ============================================
// CONFIGURATION
// ============================================
const CONFIG = {
    baseUrl: window.location.origin,
    endpoints: {
        health: '/health',
        modelsHealth: '/health/models',
        customVoice: {
            generate: '/api/v1/custom-voice/generate',
            speakers: '/api/v1/custom-voice/speakers',
            languages: '/api/v1/custom-voice/languages'
        },
        voiceDesign: {
            generate: '/api/v1/voice-design/generate'
        },
        base: {
            clone: '/api/v1/base/clone',
            createPrompt: '/api/v1/base/create-prompt',
            generateWithPrompt: '/api/v1/base/generate-with-prompt',
            uploadRefAudio: '/api/v1/base/upload-ref-audio',
            cacheStats: '/api/v1/base/cache/stats',
            cacheClear: '/api/v1/base/cache/clear'
        }
    }
};

// Speaker data (fallback if API fails)
const SPEAKERS = [
    { name: 'Vivian', description: 'Bright, slightly edgy young female voice', native_language: 'Chinese' },
    { name: 'Serena', description: 'Warm, gentle young female voice', native_language: 'Chinese' },
    { name: 'Uncle_Fu', description: 'Seasoned male voice with a low, mellow timbre', native_language: 'Chinese' },
    { name: 'Dylan', description: 'Youthful Beijing male voice, clear and natural', native_language: 'Chinese' },
    { name: 'Eric', description: 'Lively Chengdu male voice with husky brightness', native_language: 'Chinese' },
    { name: 'Ryan', description: 'Dynamic male voice with strong rhythmic drive', native_language: 'English' },
    { name: 'Aiden', description: 'Sunny American male voice with clear midrange', native_language: 'English' },
    { name: 'Ono_Anna', description: 'Playful Japanese female voice, light and nimble', native_language: 'Japanese' },
    { name: 'Sohee', description: 'Warm Korean female voice with rich emotion', native_language: 'Korean' }
];

// ============================================
// INTERNATIONALIZATION
// ============================================
const i18n = {
    en: {
        // Header
        title: 'Qwen3-TTS',
        subtitle: 'Voice Laboratory',
        // Tabs
        customVoice: 'Custom Voice',
        voiceDesign: 'Voice Design',
        voiceClone: 'Voice Clone',
        settings: 'Settings',
        // Custom Voice
        cvTitle: 'Custom Voice',
        cvDesc: 'Generate speech using 9 preset speakers with emotional control and style instructions.',
        textToSynth: 'Text to Synthesize',
        textPlaceholder: 'Hello, welcome to the Qwen3-TTS Voice Laboratory! This is a demonstration of AI-powered text-to-speech technology.',
        language: 'Language',
        selectSpeaker: 'Select Speaker',
        styleInstruction: 'Style Instruction (Optional)',
        stylePlaceholder: 'e.g., Speak cheerfully. Calm and soothing...',
        speed: 'Speed',
        generateSpeech: 'Generate Speech',
        generatedAudio: 'Generated Audio',
        genTime: 'Gen Time',
        duration: 'Duration',
        rtf: 'RTF',
        // Voice Design
        vdTitle: 'Voice Design',
        vdDesc: 'Create custom voices using natural language descriptions.',
        voiceDescription: 'Voice Description',
        voiceDescPlaceholder: 'Describe the voice you want to create...',
        examplePrompts: 'Example Prompts',
        // Voice Clone
        vcTitle: 'Voice Clone',
        vcDesc: 'Clone any voice from a reference audio sample.',
        refAudio: 'Reference Audio',
        uploadZoneText: 'Drop audio file here or click to upload',
        uploadZoneHint: 'Supports WAV, MP3, FLAC (max 5MB)',
        refTranscript: 'Reference Transcript',
        refTranscriptPlaceholder: 'Enter the exact text spoken in the reference audio...',
        xVectorMode: 'X-Vector Only Mode',
        xVectorHint: 'Skip text alignment (faster but lower quality)',
        savedPrompts: 'Saved Voice Prompts',
        createPrompt: 'Create Prompt',
        cacheStatus: 'Cache Status',
        startRecording: 'Start Recording',
        stopRecording: 'Stop Recording',
        recording: 'Recording...',
        recordedAudio: 'Recorded Audio',
        recordingComplete: 'Recording complete!',
        recordingStarted: 'Recording started...',
        microphoneError: 'Could not access microphone',
        // Settings
        settingsTitle: 'Settings',
        settingsDesc: 'Configure API access and view server status.',
        apiConfig: 'API Configuration',
        apiKey: 'API Key',
        saveApiKey: 'Save API Key',
        serverStatus: 'Server Status',
        refreshStatus: 'Refresh',
        customVoiceModel: 'CustomVoice Model',
        voiceDesignModel: 'VoiceDesign Model',
        baseModel: 'Base Model',
        cacheStats: 'Cache Statistics',
        refreshCache: 'Refresh',
        clearCache: 'Clear Cache',
        enabled: 'Enabled',
        size: 'Size',
        hitRate: 'Hit Rate',
        requests: 'Requests',
        apiDocs: 'API Documentation',
        // Toast messages
        generating: 'Generating audio...',
        generated: 'Audio generated successfully!',
        error: 'Error',
        apiKeySaved: 'API key saved',
        cacheCleared: 'Cache cleared successfully',
        noText: 'Please enter text to synthesize',
        noApiKey: 'Please set your API key in Settings',
        noVoiceDesc: 'Please enter a voice description',
        noRefAudio: 'Please upload reference audio or select a saved prompt',
        noRefText: 'Please enter the reference text or enable X-Vector Only mode'
    },
    'zh-cn': {
        // Header
        title: 'Qwen3-TTS',
        subtitle: '语音实验室',
        // Tabs
        customVoice: '自定义语音',
        voiceDesign: '语音设计',
        voiceClone: '语音克隆',
        settings: '设置',
        // Custom Voice
        cvTitle: '自定义语音',
        cvDesc: '使用9个预设角色生成语音，支持情感控制和风格指令。',
        textToSynth: '待合成文本',
        textPlaceholder: '你好，欢迎来到Qwen3-TTS语音实验室！这是一个AI驱动的文本转语音技术演示。',
        language: '语言',
        selectSpeaker: '选择角色',
        styleInstruction: '风格指令（可选）',
        stylePlaceholder: '例如：开心地说话，平静舒缓...',
        speed: '语速',
        generateSpeech: '生成语音',
        generatedAudio: '生成的音频',
        genTime: '生成时间',
        duration: '时长',
        rtf: '实时因子',
        // Voice Design
        vdTitle: '语音设计',
        vdDesc: '使用自然语言描述创建自定义语音。',
        voiceDescription: '语音描述',
        voiceDescPlaceholder: '描述你想创建的语音...',
        examplePrompts: '示例提示',
        // Voice Clone
        vcTitle: '语音克隆',
        vcDesc: '从参考音频样本克隆任意语音。',
        refAudio: '参考音频',
        uploadZoneText: '拖放音频文件到此处或点击上传',
        uploadZoneHint: '支持 WAV, MP3, FLAC（最大5MB）',
        refTranscript: '参考文本',
        refTranscriptPlaceholder: '输入参考音频中的准确文本内容...',
        xVectorMode: '仅X向量模式',
        xVectorHint: '跳过文本对齐（更快但质量较低）',
        savedPrompts: '已保存的语音提示',
        createPrompt: '创建提示',
        cacheStatus: '缓存状态',
        startRecording: '开始录音',
        stopRecording: '停止录音',
        recording: '录音中...',
        recordedAudio: '录制的音频',
        recordingComplete: '录音完成！',
        recordingStarted: '开始录音...',
        microphoneError: '无法访问麦克风',
        // Settings
        settingsTitle: '设置',
        settingsDesc: '配置API访问并查看服务器状态。',
        apiConfig: 'API配置',
        apiKey: 'API密钥',
        saveApiKey: '保存API密钥',
        serverStatus: '服务器状态',
        refreshStatus: '刷新',
        customVoiceModel: '自定义语音模型',
        voiceDesignModel: '语音设计模型',
        baseModel: '基础模型',
        cacheStats: '缓存统计',
        refreshCache: '刷新',
        clearCache: '清除缓存',
        enabled: '状态',
        size: '大小',
        hitRate: '命中率',
        requests: '请求数',
        apiDocs: 'API文档',
        // Toast messages
        generating: '正在生成音频...',
        generated: '音频生成成功！',
        error: '错误',
        apiKeySaved: 'API密钥已保存',
        cacheCleared: '缓存已清除',
        noText: '请输入待合成的文本',
        noApiKey: '请在设置中设置API密钥',
        noVoiceDesc: '请输入语音描述',
        noRefAudio: '请上传参考音频或选择已保存的提示',
        noRefText: '请输入参考文本或启用仅X向量模式'
    }
};

// ============================================
// STATE
// ============================================

// Default API key for demo (can be overridden in Settings)
const DEFAULT_API_KEY = 'your-api-key-1';

const state = {
    apiKey: localStorage.getItem('qwen-tts-api-key') || DEFAULT_API_KEY,
    language: localStorage.getItem('qwen-tts-lang') || 'en',
    selectedSpeaker: 'Ryan',
    savedPrompts: JSON.parse(localStorage.getItem('qwen-tts-prompts') || '[]'),
    uploadedAudio: null,
    uploadedAudioBase64: null,
    selectedPromptId: null
};

/**
 * Translation helper function
 */
function t(key) {
    return i18n[state.language]?.[key] || i18n.en[key] || key;
}

/**
 * Switch language and update all UI text
 */
function switchLanguage(lang) {
    state.language = lang;
    localStorage.setItem('qwen-tts-lang', lang);

    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
            el.placeholder = t(key);
        } else {
            el.textContent = t(key);
        }
    });

    // Update language buttons
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Get headers with API key
 */
function getHeaders(contentType = 'application/json') {
    const headers = {};
    if (contentType) {
        headers['Content-Type'] = contentType;
    }
    if (state.apiKey) {
        headers['X-API-Key'] = state.apiKey;
    }
    return headers;
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    overlay.style.display = show ? 'flex' : 'none';
}

/**
 * Convert file to base64
 */
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            // Remove data URL prefix (e.g., "data:audio/wav;base64,")
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
    });
}

/**
 * Format file size
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Format duration
 */
function formatDuration(seconds) {
    if (seconds < 60) return seconds.toFixed(1) + 's';
    const mins = Math.floor(seconds / 60);
    const secs = (seconds % 60).toFixed(1);
    return `${mins}m ${secs}s`;
}

/**
 * Generate waveform bars
 */
function generateWaveformBars(container, count = 50) {
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const bar = document.createElement('div');
        bar.className = 'waveform-bar';
        bar.style.height = `${Math.random() * 40 + 10}px`;
        container.appendChild(bar);
    }
}

/**
 * Animate waveform with audio
 */
function animateWaveform(container, audioElement) {
    const bars = container.querySelectorAll('.waveform-bar');
    let animationFrame;

    const animate = () => {
        if (audioElement.paused) {
            bars.forEach(bar => bar.classList.remove('active'));
            return;
        }

        bars.forEach((bar, i) => {
            const height = Math.random() * 50 + 10;
            bar.style.height = height + 'px';
            bar.classList.toggle('active', Math.random() > 0.5);
        });

        animationFrame = requestAnimationFrame(animate);
    };

    audioElement.onplay = () => {
        animate();
    };

    audioElement.onpause = () => {
        cancelAnimationFrame(animationFrame);
        bars.forEach(bar => bar.classList.remove('active'));
    };

    audioElement.onended = () => {
        cancelAnimationFrame(animationFrame);
        bars.forEach(bar => bar.classList.remove('active'));
    };
}

// ============================================
// API FUNCTIONS
// ============================================

/**
 * Check server health
 */
async function checkHealth() {
    const statusDot = document.getElementById('status-dot');
    const statusText = document.getElementById('status-text');

    try {
        statusDot.className = 'status-dot loading';
        statusText.textContent = 'Connecting...';

        const response = await fetch(CONFIG.endpoints.health);
        const data = await response.json();

        statusDot.className = 'status-dot';
        statusText.textContent = `v${data.version}`;
        return true;
    } catch (error) {
        statusDot.className = 'status-dot error';
        statusText.textContent = 'Offline';
        return false;
    }
}

/**
 * Check models health
 */
async function checkModelsHealth() {
    try {
        const response = await fetch(CONFIG.endpoints.modelsHealth);
        const data = await response.json();

        // Update status cards
        updateModelStatus('status-custom-voice', data.custom_voice_loaded);
        updateModelStatus('status-voice-design', data.voice_design_loaded);
        updateModelStatus('status-base', data.base_loaded);

        return data;
    } catch (error) {
        console.error('Failed to check models health:', error);
        return null;
    }
}

function updateModelStatus(elementId, loaded) {
    const element = document.getElementById(elementId);
    element.textContent = loaded ? 'Loaded' : 'Not Loaded';
    element.className = loaded ? 'status-card-value loaded' : 'status-card-value not-loaded';
}

/**
 * Fetch cache stats
 */
async function fetchCacheStats() {
    try {
        const response = await fetch(CONFIG.endpoints.base.cacheStats, {
            headers: getHeaders(null)
        });

        if (!response.ok) {
            throw new Error('Failed to fetch cache stats');
        }

        const data = await response.json();

        document.getElementById('cache-enabled').textContent = data.enabled ? 'Enabled' : 'Disabled';
        document.getElementById('cache-size').textContent = `${data.size} / ${data.max_size}`;
        document.getElementById('cache-hit-rate').textContent = `${data.hit_rate_percent?.toFixed(1) || 0}%`;
        document.getElementById('cache-requests').textContent = data.total_requests || 0;

        return data;
    } catch (error) {
        console.error('Failed to fetch cache stats:', error);
        return null;
    }
}

/**
 * Clear cache
 */
async function clearCache() {
    try {
        const response = await fetch(CONFIG.endpoints.base.cacheClear, {
            method: 'POST',
            headers: getHeaders(null)
        });

        if (!response.ok) {
            throw new Error('Failed to clear cache');
        }

        showToast('Cache cleared successfully', 'success');
        fetchCacheStats();
    } catch (error) {
        showToast('Failed to clear cache', 'error');
    }
}

/**
 * Generate Custom Voice
 */
async function generateCustomVoice() {
    const text = document.getElementById('cv-text').value.trim();
    const language = document.getElementById('cv-language').value;
    const speed = parseFloat(document.getElementById('cv-speed').value);
    const instruct = document.getElementById('cv-instruct').value.trim() || null;

    if (!text) {
        showToast('Please enter text to synthesize', 'warning');
        return;
    }

    if (!state.apiKey) {
        showToast('Please set your API key in Settings', 'warning');
        return;
    }

    const btn = document.getElementById('cv-generate-btn');
    btn.classList.add('loading');
    btn.disabled = true;


    try {
        const startTime = performance.now();

        const response = await fetch(CONFIG.endpoints.customVoice.generate, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                text,
                language,
                speaker: state.selectedSpeaker,
                instruct,
                speed,
                response_format: 'base64'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        const data = await response.json();
        const genTime = (performance.now() - startTime) / 1000;

        // Play audio
        playAudio('cv', data.audio, data.sample_rate, {
            generationTime: genTime,
            headers: Object.fromEntries(response.headers.entries())
        });

        showToast('Audio generated successfully!', 'success');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;

    }
}

/**
 * Generate Voice Design
 */
async function generateVoiceDesign() {
    const text = document.getElementById('vd-text').value.trim();
    const language = document.getElementById('vd-language').value;
    const speed = parseFloat(document.getElementById('vd-speed').value);
    const instruct = document.getElementById('vd-instruct').value.trim();

    if (!text) {
        showToast('Please enter text to synthesize', 'warning');
        return;
    }

    if (!instruct) {
        showToast('Please enter a voice description', 'warning');
        return;
    }

    if (!state.apiKey) {
        showToast('Please set your API key in Settings', 'warning');
        return;
    }

    const btn = document.getElementById('vd-generate-btn');
    btn.classList.add('loading');
    btn.disabled = true;


    try {
        const startTime = performance.now();

        const response = await fetch(CONFIG.endpoints.voiceDesign.generate, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                text,
                language,
                instruct,
                speed,
                response_format: 'base64'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        const data = await response.json();
        const genTime = (performance.now() - startTime) / 1000;

        // Play audio
        playAudio('vd', data.audio, data.sample_rate, {
            generationTime: genTime,
            headers: Object.fromEntries(response.headers.entries())
        });

        showToast('Voice design generated successfully!', 'success');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;

    }
}

/**
 * Clone Voice
 */
async function cloneVoice() {
    const text = document.getElementById('vc-text').value.trim();
    const language = document.getElementById('vc-language').value;
    const speed = parseFloat(document.getElementById('vc-speed').value);
    const refText = document.getElementById('vc-ref-text').value.trim();
    const xVectorOnly = document.getElementById('vc-xvector-toggle').classList.contains('active');

    if (!text) {
        showToast('Please enter text to synthesize', 'warning');
        return;
    }

    if (!state.apiKey) {
        showToast('Please set your API key in Settings', 'warning');
        return;
    }

    // Check if we're using a saved prompt
    if (state.selectedPromptId) {
        return generateWithPrompt(text, language, speed);
    }

    // Check for uploaded audio
    if (!state.uploadedAudioBase64) {
        showToast('Please upload reference audio or select a saved prompt', 'warning');
        return;
    }

    if (!xVectorOnly && !refText) {
        showToast('Please enter the reference text (transcript) or enable X-Vector Only mode', 'warning');
        return;
    }

    const btn = document.getElementById('vc-generate-btn');
    btn.classList.add('loading');
    btn.disabled = true;


    try {
        const startTime = performance.now();

        const response = await fetch(CONFIG.endpoints.base.clone, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                text,
                language,
                ref_audio_base64: state.uploadedAudioBase64,
                ref_text: xVectorOnly ? null : refText,
                x_vector_only_mode: xVectorOnly,
                speed,
                response_format: 'base64'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Clone failed');
        }

        const data = await response.json();
        const genTime = (performance.now() - startTime) / 1000;

        // Play audio
        playAudio('vc', data.audio, data.sample_rate, {
            generationTime: genTime,
            headers: Object.fromEntries(response.headers.entries())
        });

        showToast('Voice cloned successfully!', 'success');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;

    }
}

/**
 * Create voice prompt
 */
async function createVoicePrompt() {
    const refText = document.getElementById('vc-ref-text').value.trim();
    const xVectorOnly = document.getElementById('vc-xvector-toggle').classList.contains('active');

    if (!state.uploadedAudioBase64) {
        showToast('Please upload reference audio first', 'warning');
        return;
    }

    if (!xVectorOnly && !refText) {
        showToast('Please enter the reference text or enable X-Vector Only mode', 'warning');
        return;
    }

    if (!state.apiKey) {
        showToast('Please set your API key in Settings', 'warning');
        return;
    }

    const btn = document.getElementById('vc-create-prompt-btn');
    btn.classList.add('loading');
    btn.disabled = true;

    try {
        const response = await fetch(CONFIG.endpoints.base.createPrompt, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                ref_audio_base64: state.uploadedAudioBase64,
                ref_text: xVectorOnly ? null : refText,
                x_vector_only_mode: xVectorOnly
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create prompt');
        }

        const data = await response.json();

        // Save prompt
        state.savedPrompts.push({
            id: data.prompt_id,
            createdAt: new Date().toISOString()
        });
        localStorage.setItem('qwen-tts-prompts', JSON.stringify(state.savedPrompts));
        renderSavedPrompts();

        showToast(`Prompt created: ${data.prompt_id.slice(0, 8)}...`, 'success');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

/**
 * Generate with saved prompt
 */
async function generateWithPrompt(text, language, speed) {
    if (!state.selectedPromptId) return;

    const btn = document.getElementById('vc-generate-btn');
    btn.classList.add('loading');
    btn.disabled = true;


    try {
        const startTime = performance.now();

        const response = await fetch(CONFIG.endpoints.base.generateWithPrompt, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                text,
                language,
                prompt_id: state.selectedPromptId,
                response_format: 'base64'
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Generation failed');
        }

        const data = await response.json();
        const genTime = (performance.now() - startTime) / 1000;

        playAudio('vc', data.audio, data.sample_rate, {
            generationTime: genTime,
            headers: Object.fromEntries(response.headers.entries())
        });

        showToast('Generated with saved prompt!', 'success');

    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        btn.classList.remove('loading');
        btn.disabled = false;

    }
}

/**
 * Play audio from base64
 */
function playAudio(prefix, base64Audio, sampleRate, metrics = {}) {
    const container = document.getElementById(`${prefix}-audio-container`);
    const player = document.getElementById(`${prefix}-audio-player`);
    const waveformContainer = document.getElementById(`${prefix}-waveform`);

    // Create blob URL
    const audioBlob = base64ToBlob(base64Audio, 'audio/wav');
    const audioUrl = URL.createObjectURL(audioBlob);

    // Set audio source
    player.src = audioUrl;

    // Generate waveform
    generateWaveformBars(waveformContainer);
    animateWaveform(waveformContainer, player);

    // Show container
    container.classList.add('visible');

    // Update metrics
    if (metrics.generationTime) {
        document.getElementById(`${prefix}-metric-time`).textContent = metrics.generationTime.toFixed(2) + 's';
    }

    // Parse headers for additional metrics
    if (metrics.headers) {
        if (metrics.headers['x-audio-duration']) {
            document.getElementById(`${prefix}-metric-duration`).textContent =
                parseFloat(metrics.headers['x-audio-duration']).toFixed(2) + 's';
        }
        if (metrics.headers['x-rtf']) {
            document.getElementById(`${prefix}-metric-rtf`).textContent =
                parseFloat(metrics.headers['x-rtf']).toFixed(2) + 'x';
        }
        if (metrics.headers['x-cache-status'] && prefix === 'vc') {
            document.getElementById('vc-metric-cache').textContent = metrics.headers['x-cache-status'];
        }
    }

    // Auto-play
    player.play().catch(() => { });
}

/**
 * Convert base64 to blob
 */
function base64ToBlob(base64, mimeType) {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
}

// ============================================
// UI COMPONENTS
// ============================================

/**
 * Render speaker grid
 */
function renderSpeakerGrid() {
    const grid = document.getElementById('cv-speaker-grid');
    grid.innerHTML = '';

    SPEAKERS.forEach(speaker => {
        const card = document.createElement('div');
        card.className = `speaker-card${speaker.name === state.selectedSpeaker ? ' selected' : ''}`;
        card.innerHTML = `
      <div class="speaker-name">${speaker.name.replace('_', ' ')}</div>
      <div class="speaker-lang">${speaker.native_language}</div>
      <div class="speaker-desc">${speaker.description}</div>
    `;
        card.onclick = () => selectSpeaker(speaker.name, card);
        grid.appendChild(card);
    });
}

function selectSpeaker(name, card) {
    state.selectedSpeaker = name;
    document.querySelectorAll('.speaker-card').forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
}

/**
 * Render saved prompts
 */
function renderSavedPrompts() {
    const list = document.getElementById('vc-prompts-list');

    if (state.savedPrompts.length === 0) {
        list.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No saved prompts yet</p>';
        return;
    }

    list.innerHTML = state.savedPrompts.map(prompt => `
    <div class="saved-prompt-item${prompt.id === state.selectedPromptId ? ' selected' : ''}" data-id="${prompt.id}">
      <div>
        <div class="saved-prompt-id">ID: ${prompt.id.slice(0, 8)}...</div>
        <div style="font-size: 0.625rem; color: var(--text-muted);">
          ${new Date(prompt.createdAt).toLocaleDateString()}
        </div>
      </div>
      <button class="saved-prompt-delete" data-id="${prompt.id}">✕</button>
    </div>
  `).join('');

    // Add click handlers
    list.querySelectorAll('.saved-prompt-item').forEach(item => {
        item.onclick = (e) => {
            if (e.target.classList.contains('saved-prompt-delete')) return;
            selectPrompt(item.dataset.id);
        };
    });

    list.querySelectorAll('.saved-prompt-delete').forEach(btn => {
        btn.onclick = (e) => {
            e.stopPropagation();
            deletePrompt(btn.dataset.id);
        };
    });
}

function selectPrompt(id) {
    state.selectedPromptId = state.selectedPromptId === id ? null : id;
    renderSavedPrompts();

    if (state.selectedPromptId) {
        showToast('Using saved prompt for generation', 'info');
    }
}

function deletePrompt(id) {
    state.savedPrompts = state.savedPrompts.filter(p => p.id !== id);
    localStorage.setItem('qwen-tts-prompts', JSON.stringify(state.savedPrompts));
    if (state.selectedPromptId === id) {
        state.selectedPromptId = null;
    }
    renderSavedPrompts();
    showToast('Prompt deleted', 'info');
}

// ============================================
// EVENT HANDLERS
// ============================================

/**
 * Initialize tab navigation
 */
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');

    tabBtns.forEach(btn => {
        btn.onclick = () => {
            const tabId = btn.dataset.tab;

            // Update active states
            tabBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-selected', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-selected', 'true');

            // Show/hide panels
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
            });
            document.getElementById(`panel-${tabId}`).classList.add('active');
        };
    });
}

/**
 * Initialize character counters
 */
function initCharCounters() {
    const counters = [
        { input: 'cv-text', counter: 'cv-char-count' },
        { input: 'vd-text', counter: 'vd-char-count' },
        { input: 'vc-text', counter: 'vc-char-count' }
    ];

    counters.forEach(({ input, counter }) => {
        const inputEl = document.getElementById(input);
        const counterEl = document.getElementById(counter);

        const update = () => {
            counterEl.textContent = inputEl.value.length;
        };

        inputEl.oninput = update;
        update(); // Initial count
    });
}

/**
 * Initialize speed sliders
 */
function initSpeedSliders() {
    const sliders = ['cv-speed', 'vd-speed', 'vc-speed'];

    sliders.forEach(id => {
        const slider = document.getElementById(id);
        const display = document.getElementById(`${id}-value`);

        slider.oninput = () => {
            display.textContent = parseFloat(slider.value).toFixed(1) + 'x';
        };
    });
}

/**
 * Initialize quick instruction buttons
 */
function initQuickInstructions() {
    document.querySelectorAll('.quick-instruction').forEach(btn => {
        btn.onclick = () => {
            document.getElementById('cv-instruct').value = btn.dataset.value;
        };
    });
}

/**
 * Initialize voice design example prompts
 */
function initExamplePrompts() {
    document.querySelectorAll('.example-prompt').forEach(btn => {
        btn.onclick = () => {
            document.getElementById('vd-instruct').value = btn.dataset.instruct;
        };
    });
}

/**
 * Initialize file upload
 */
function initFileUpload() {
    const zone = document.getElementById('vc-upload-zone');
    const input = document.getElementById('vc-file-input');
    const preview = document.getElementById('vc-upload-preview');
    const fileName = document.getElementById('vc-file-name');
    const fileSize = document.getElementById('vc-file-size');
    const refAudio = document.getElementById('vc-ref-audio');

    // Click to upload
    zone.onclick = () => input.click();

    // Drag and drop
    zone.ondragover = (e) => {
        e.preventDefault();
        zone.classList.add('dragover');
    };

    zone.ondragleave = () => {
        zone.classList.remove('dragover');
    };

    zone.ondrop = async (e) => {
        e.preventDefault();
        zone.classList.remove('dragover');

        const file = e.dataTransfer.files[0];
        if (file) await handleAudioUpload(file);
    };

    // File input change
    input.onchange = async () => {
        if (input.files[0]) {
            await handleAudioUpload(input.files[0]);
        }
    };

    async function handleAudioUpload(file) {
        // Validate file type
        if (!file.type.startsWith('audio/')) {
            showToast('Please upload an audio file', 'error');
            return;
        }

        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            showToast('File too large (max 5MB)', 'error');
            return;
        }

        try {
            state.uploadedAudio = file;
            state.uploadedAudioBase64 = await fileToBase64(file);
            state.selectedPromptId = null; // Clear selected prompt

            // Update preview
            fileName.textContent = file.name;
            fileSize.textContent = formatFileSize(file.size);
            refAudio.src = URL.createObjectURL(file);
            preview.classList.add('visible');

            renderSavedPrompts(); // Update selection
            showToast('Audio uploaded successfully', 'success');
        } catch (error) {
            showToast('Failed to process audio file', 'error');
        }
    }
}

/**
 * Initialize voice recording
 */
function initRecording() {
    const recordBtn = document.getElementById('vc-record-btn');
    const stopBtn = document.getElementById('vc-stop-btn');
    const indicator = document.getElementById('vc-recording-indicator');
    const timeDisplay = document.getElementById('vc-record-time');
    const preview = document.getElementById('vc-upload-preview');
    const fileName = document.getElementById('vc-file-name');
    const fileSize = document.getElementById('vc-file-size');
    const refAudio = document.getElementById('vc-ref-audio');

    let mediaRecorder = null;
    let audioChunks = [];
    let recordingTimer = null;
    let recordingSeconds = 0;

    recordBtn.onclick = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            audioChunks = [];
            recordingSeconds = 0;

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    audioChunks.push(e.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const audioFile = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });

                // Convert to base64
                state.uploadedAudio = audioFile;
                state.uploadedAudioBase64 = await fileToBase64(audioFile);
                state.selectedPromptId = null;

                // Update preview
                fileName.textContent = t('recordedAudio') || 'Recorded Audio';
                fileSize.textContent = formatFileSize(audioBlob.size);
                refAudio.src = URL.createObjectURL(audioBlob);
                preview.classList.add('visible');

                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());

                showToast(t('recordingComplete') || 'Recording complete!', 'success');
            };

            mediaRecorder.start();

            // Update UI
            recordBtn.style.display = 'none';
            stopBtn.style.display = 'flex';
            indicator.style.display = 'flex';

            // Start timer
            recordingTimer = setInterval(() => {
                recordingSeconds++;
                const mins = Math.floor(recordingSeconds / 60);
                const secs = recordingSeconds % 60;
                timeDisplay.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;

                // Auto-stop at 60 seconds
                if (recordingSeconds >= 60) {
                    stopBtn.click();
                }
            }, 1000);

            showToast(t('recordingStarted') || 'Recording started...', 'info');
        } catch (error) {
            console.error('Recording error:', error);
            showToast(t('microphoneError') || 'Could not access microphone', 'error');
        }
    };

    stopBtn.onclick = () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
        }

        // Reset UI
        clearInterval(recordingTimer);
        recordBtn.style.display = 'flex';
        stopBtn.style.display = 'none';
        indicator.style.display = 'none';
        timeDisplay.textContent = '0:00';
    };
}

/**
 * Initialize toggle switches
 */
function initToggles() {
    const toggle = document.getElementById('vc-xvector-toggle');
    toggle.onclick = () => {
        toggle.classList.toggle('active');
    };
}

/**
 * Initialize API key input
 */
function initApiKey() {
    const input = document.getElementById('api-key');
    const toggle = document.getElementById('api-key-toggle');
    const saveBtn = document.getElementById('save-api-key');

    // Load saved key
    input.value = state.apiKey;

    // Toggle visibility
    toggle.onclick = () => {
        input.type = input.type === 'password' ? 'text' : 'password';
        toggle.textContent = input.type === 'password' ? '👁️' : '🙈';
    };

    // Save key
    saveBtn.onclick = () => {
        state.apiKey = input.value.trim();
        localStorage.setItem('qwen-tts-api-key', state.apiKey);
        showToast('API key saved', 'success');
    };
}

/**
 * Initialize button handlers
 */
function initButtons() {
    // Custom Voice
    document.getElementById('cv-generate-btn').onclick = generateCustomVoice;

    // Voice Design
    document.getElementById('vd-generate-btn').onclick = generateVoiceDesign;

    // Voice Clone
    document.getElementById('vc-generate-btn').onclick = cloneVoice;
    document.getElementById('vc-create-prompt-btn').onclick = createVoicePrompt;

    // Settings
    document.getElementById('refresh-status').onclick = () => {
        checkHealth();
        checkModelsHealth();
    };
    document.getElementById('refresh-cache').onclick = fetchCacheStats;
    document.getElementById('clear-cache').onclick = clearCache;
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize UI components
    initTabs();
    initCharCounters();
    initSpeedSliders();
    initQuickInstructions();
    initExamplePrompts();
    initFileUpload();
    initRecording();
    initToggles();
    initApiKey();
    initButtons();

    // Render components
    renderSpeakerGrid();
    renderSavedPrompts();

    // Initialize language
    switchLanguage(state.language);

    // Initial API checks
    checkHealth();
    checkModelsHealth();
    fetchCacheStats();

    console.log('🎙️ Qwen3-TTS Demo initialized');
});
