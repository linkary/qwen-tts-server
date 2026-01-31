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
// STATE
// ============================================

// Default API key for demo (can be overridden in Settings)
const DEFAULT_API_KEY = 'your-api-key-1';

const state = {
    apiKey: localStorage.getItem('qwen-tts-api-key') || DEFAULT_API_KEY,
    selectedSpeaker: 'Ryan',
    savedPrompts: JSON.parse(localStorage.getItem('qwen-tts-prompts') || '[]'),
    uploadedAudio: null,
    uploadedAudioBase64: null,
    selectedPromptId: null
};

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
    showLoading(true);

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
        showLoading(false);
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
    showLoading(true);

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
        showLoading(false);
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
    showLoading(true);

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
        showLoading(false);
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
    showLoading(true);

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
        showLoading(false);
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
    initToggles();
    initApiKey();
    initButtons();

    // Render components
    renderSpeakerGrid();
    renderSavedPrompts();

    // Initial API checks
    checkHealth();
    checkModelsHealth();
    fetchCacheStats();

    console.log('🎙️ Qwen3-TTS Demo initialized');
});
