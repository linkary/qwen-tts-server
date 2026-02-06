import React, { useState } from 'react';
import { Card, CardHeader } from '../../ui/Card';
import { FormTextarea } from '../../forms/FormTextarea';
import { FormSelect } from '../../forms/FormSelect';
import { RangeSlider } from '../../forms/RangeSlider';
import { Toggle } from '../../forms/Toggle';
import { Button } from '../../ui/Button';
import { AudioPlayer } from '../../audio/AudioPlayer';
import { AudioUpload } from './AudioUpload';
import { AudioRecorder } from './AudioRecorder';
import { SavedPrompts } from './SavedPrompts';
import { useAppContext } from '../../../context/AppContext';
import { useToast } from '../../../context/ToastContext';
import { useTranslation } from '../../../i18n/I18nContext';
import { useI18n } from '../../../i18n/I18nContext';
import { cloneVoice, createVoicePrompt, generateWithPrompt } from '../../../services/api';
import { base64ToBlob } from '../../../utils/audio';
import { RECORDING_PROMPTS } from '../../../config/recordingPrompts';
import type { AudioMetrics } from '../../../types/audio';
import { cn } from '../../../utils/cn';

export function VoiceCloneTab() {
  const t = useTranslation();
  const { language } = useI18n();
  const { 
    apiKey, 
    savedPrompts, 
    selectedPromptId,
    setSelectedPromptId,
    addSavedPrompt,
    removeSavedPrompt,
    uploadedFileBase64,
    setUploadedFileBase64,
    recordedAudioBase64,
    setRecordedAudioBase64,
  } = useAppContext();
  const { showToast } = useToast();

  const [activeSubTab, setActiveSubTab] = useState<'upload' | 'record'>('upload');
  const [refText, setRefText] = useState('');
  const [xVectorOnly, setXVectorOnly] = useState(false);
  const [text, setText] = useState(t('defaultTextVoiceClone'));
  const [targetLanguage, setTargetLanguage] = useState('English');
  const [speed, setSpeed] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreatingPrompt, setIsCreatingPrompt] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<AudioMetrics>({});

  const handleAudioUploaded = (base64: string) => {
    setUploadedFileBase64(base64);
    setSelectedPromptId(null);
  };

  const handleAudioRecorded = (base64: string) => {
    setRecordedAudioBase64(base64);
    setSelectedPromptId(null);
    // Auto-fill transcript
    setRefText(RECORDING_PROMPTS[language] || RECORDING_PROMPTS.en);
  };

  const handleCreatePrompt = async () => {
    const audioBase64 = activeSubTab === 'upload' ? uploadedFileBase64 : recordedAudioBase64;

    if (!audioBase64) {
      showToast('Please upload or record reference audio first', 'warning');
      return;
    }

    if (!xVectorOnly && !refText.trim()) {
      showToast(t('noRefText'), 'warning');
      return;
    }

    if (!apiKey) {
      showToast(t('noApiKey'), 'warning');
      return;
    }

    setIsCreatingPrompt(true);

    try {
      const result = await createVoicePrompt(
        {
          ref_audio_base64: audioBase64,
          ref_text: xVectorOnly ? undefined : refText,
          x_vector_only_mode: xVectorOnly,
        },
        apiKey
      );

      addSavedPrompt({
        id: result.prompt_id,
        createdAt: new Date().toISOString(),
      });

      showToast(`Prompt created: ${result.prompt_id.slice(0, 8)}...`, 'success');
    } catch (error) {
      showToast((error as Error).message, 'error');
    } finally {
      setIsCreatingPrompt(false);
    }
  };

  const handleGenerate = async () => {
    if (!text.trim()) {
      showToast(t('noText'), 'warning');
      return;
    }

    if (!apiKey) {
      showToast(t('noApiKey'), 'warning');
      return;
    }

    // Check if using saved prompt
    if (selectedPromptId) {
      return handleGenerateWithPrompt();
    }

    // Otherwise clone with direct audio
    const audioBase64 = activeSubTab === 'upload' ? uploadedFileBase64 : recordedAudioBase64;

    if (!audioBase64) {
      showToast(t('noRefAudio'), 'warning');
      return;
    }

    if (!xVectorOnly && !refText.trim()) {
      showToast(t('noRefText'), 'warning');
      return;
    }

    setIsLoading(true);
    const startTime = performance.now();

    try {
      const { data, headers } = await cloneVoice(
        {
          text,
          language: targetLanguage,
          ref_audio_base64: audioBase64,
          ref_text: xVectorOnly ? undefined : refText,
          x_vector_only_mode: xVectorOnly,
          speed,
          response_format: 'base64',
        },
        apiKey
      );

      const genTime = (performance.now() - startTime) / 1000;
      const audioBlob = base64ToBlob(data.audio, 'audio/wav');
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      setMetrics({
        generationTime: genTime,
        audioDuration: parseFloat(headers.get('x-audio-duration') || '0'),
        rtf: parseFloat(headers.get('x-rtf') || '0'),
        cacheStatus: headers.get('x-cache-status') || undefined,
      });

      showToast('Voice cloned successfully!', 'success');
    } catch (error) {
      showToast((error as Error).message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateWithPrompt = async () => {
    if (!selectedPromptId) return;

    setIsLoading(true);
    const startTime = performance.now();

    try {
      const { data, headers } = await generateWithPrompt(
        {
          text,
          language: targetLanguage,
          prompt_id: selectedPromptId,
          speed,
          response_format: 'base64',
        },
        apiKey
      );

      const genTime = (performance.now() - startTime) / 1000;
      const audioBlob = base64ToBlob(data.audio, 'audio/wav');
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      setMetrics({
        generationTime: genTime,
        audioDuration: parseFloat(headers.get('x-audio-duration') || '0'),
        rtf: parseFloat(headers.get('x-rtf') || '0'),
        cacheStatus: headers.get('x-cache-status') || undefined,
      });

      showToast('Generated with saved prompt!', 'success');
    } catch (error) {
      showToast((error as Error).message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptSelect = (id: string) => {
    setSelectedPromptId(selectedPromptId === id ? null : id);
    if (selectedPromptId !== id) {
      showToast('Using saved prompt for generation', 'info');
    }
  };

  const handlePromptDelete = (id: string) => {
    removeSavedPrompt(id);
    showToast('Prompt deleted', 'info');
  };

  return (
    <div>
      <div className="mb-xl">
        <h1 className="text-2xl mb-sm text-text-primary">{t('vcTitle')}</h1>
        <p className="text-text-secondary text-base max-w-[600px]">{t('vcDesc')}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-xl">
        {/* Left Column: Reference Audio */}
        <div>
          <Card>
            <CardHeader>
              <h3 className="font-display text-lg font-semibold text-text-primary">
                {t('refAudio')}
              </h3>
            </CardHeader>

            {/* Sub-tabs */}
            <div className="flex border-b border-border-subtle mb-md">
              <button
                onClick={() => setActiveSubTab('upload')}
                className={cn(
                  'flex-1 py-sm border-b-2 transition-all font-medium',
                  activeSubTab === 'upload'
                    ? 'border-accent-cyan text-accent-cyan bg-[rgba(255,255,255,0.05)]'
                    : 'border-transparent text-text-secondary hover:text-text-primary hover:bg-[rgba(255,255,255,0.02)]'
                )}
              >
                {t('vcUploadFile')}
              </button>
              <button
                onClick={() => setActiveSubTab('record')}
                className={cn(
                  'flex-1 py-sm border-b-2 transition-all font-medium',
                  activeSubTab === 'record'
                    ? 'border-accent-cyan text-accent-cyan bg-[rgba(255,255,255,0.05)]'
                    : 'border-transparent text-text-secondary hover:text-text-primary hover:bg-[rgba(255,255,255,0.02)]'
                )}
              >
                {t('vcMicrophone')}
              </button>
            </div>

            {/* Tab Content */}
            <div className="animate-fadeIn">
              {activeSubTab === 'upload' ? (
                <AudioUpload onAudioUploaded={handleAudioUploaded} />
              ) : (
                <AudioRecorder onAudioRecorded={handleAudioRecorded} />
              )}
            </div>

            {/* Reference Text */}
            <div className="mt-lg">
              <FormTextarea
                 label={`${t('refTranscript')} (${t('vcReferenceTranscript')})`}
                value={refText}
                onChange={(e) => setRefText(e.target.value)}
                placeholder={t('vcEnterRefText')}
                maxLength={1000}
              />
            </div>

            {/* X-Vector Mode */}
            <div className="mb-lg">
              <Toggle
                checked={xVectorOnly}
                onChange={setXVectorOnly}
                label={t('vcXVectorMode')}
              />
            </div>

            {/* Create Prompt Button */}
            <Button
              variant="secondary"
              isLoading={isCreatingPrompt}
              onClick={handleCreatePrompt}
              className="w-full"
            >
              {t('vcSaveToLibrary')}
            </Button>
            <p className="text-center text-xs text-text-muted mt-xs mb-md">
              {t('vcSaveHint')}
            </p>

            {/* Saved Prompts */}
            <SavedPrompts
              prompts={savedPrompts}
              selectedPromptId={selectedPromptId}
              onSelectPrompt={handlePromptSelect}
              onDeletePrompt={handlePromptDelete}
            />
          </Card>
        </div>

        {/* Right Column: Generation */}
        <div>
          <Card>
            <CardHeader>
              <h3 className="font-display text-lg font-semibold text-text-primary">
                {t('vcGenerateWithCloned')}
              </h3>
            </CardHeader>

            <FormTextarea
              label={t('textToSynth')}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t('vcEnterGenText')}
              maxLength={1000}
            />
            <div className="mb-lg" />

            <FormSelect
              label={t('language')}
              value={targetLanguage}
              onChange={(e) => setTargetLanguage(e.target.value)}
            >
              <option value="Auto">{t('langAuto')}</option>
              <option value="Chinese">{t('langChinese')}</option>
              <option value="English">{t('langEnglish')}</option>
              <option value="Japanese">{t('langJapanese')}</option>
              <option value="Korean">{t('langKorean')}</option>
              <option value="German">{t('langGerman')}</option>
              <option value="French">{t('langFrench')}</option>
              <option value="Russian">{t('langRussian')}</option>
              <option value="Portuguese">{t('langPortuguese')}</option>
              <option value="Spanish">{t('langSpanish')}</option>
              <option value="Italian">{t('langItalian')}</option>
            </FormSelect>
            <div className="mb-lg" />

            <RangeSlider
              label={t('speed')}
              value={speed}
              onChange={(e) => setSpeed(parseFloat(e.target.value))}
              min={0.5}
              max={2}
              step={0.1}
            />

            <Button
              variant="primary"
              isLoading={isLoading}
              onClick={handleGenerate}
              className="w-full mt-lg"
            >
              <span>▶</span> {t('vcCloneAndGenerate')}
            </Button>
          </Card>

          <AudioPlayer
            audioUrl={audioUrl}
            metrics={metrics}
            title="Cloned Voice Output"
            showCache={true}
          />
        </div>
      </div>
    </div>
  );
}
