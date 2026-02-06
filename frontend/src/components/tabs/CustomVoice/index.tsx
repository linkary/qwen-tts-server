import React, { useState } from 'react';
import { FormTextarea } from '../../forms/FormTextarea';
import { FormSelect } from '../../forms/FormSelect';
import { FormInput } from '../../forms/FormInput';
import { RangeSlider } from '../../forms/RangeSlider';
import { Button } from '../../ui/Button';
import { AudioPlayer } from '../../audio/AudioPlayer';
import { SpeakerGrid } from './SpeakerGrid';
import { QuickInstructions } from './QuickInstructions';
import { useAppContext } from '../../../context/AppContext';
import { useToast } from '../../../context/ToastContext';
import { useTranslation } from '../../../i18n/I18nContext';
import { generateCustomVoice } from '../../../services/api';
import { base64ToBlob } from '../../../utils/audio';
import type { AudioMetrics } from '../../../types/audio';

export function CustomVoiceTab() {
  const t = useTranslation();
  const { apiKey, selectedSpeaker, setSelectedSpeaker } = useAppContext();
  const { showToast } = useToast();

  const [text, setText] = useState(t('defaultTextCustomVoice'));
  const [language, setLanguage] = useState('English');
  const [instruct, setInstruct] = useState('');
  const [speed, setSpeed] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<AudioMetrics>({});

  const handleGenerate = async () => {
    if (!text.trim()) {
      showToast(t('noText'), 'warning');
      return;
    }

    if (!apiKey) {
      showToast(t('noApiKey'), 'warning');
      return;
    }

    setIsLoading(true);
    const startTime = performance.now();

    try {
      const { data, headers } = await generateCustomVoice(
        {
          text,
          language,
          speaker: selectedSpeaker,
          instruct: instruct || undefined,
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
      });

      showToast(t('generated'), 'success');
    } catch (error) {
      showToast((error as Error).message, 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-xl">
        <h1 className="text-2xl mb-sm text-text-primary">{t('cvTitle')}</h1>
        <p className="text-text-secondary text-base max-w-[600px]">{t('cvDesc')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-xl">
        {/* Left Column */}
        <div>
          <FormTextarea
            label={t('textToSynth')}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder={t('textPlaceholder')}
            maxLength={1000}
          />
          <div className="mb-lg" />

          <FormSelect
            label={t('language')}
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
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

          <div className="mb-lg">
            <FormInput
              label={t('styleInstruction')}
              value={instruct}
              onChange={(e) => setInstruct(e.target.value)}
              placeholder={t('stylePlaceholder')}
            />
            <QuickInstructions onSelect={setInstruct} />
          </div>

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
            <span>▶</span> {t('generateSpeech')}
          </Button>
        </div>

        {/* Right Column */}
        <div>
          <SpeakerGrid
            selectedSpeaker={selectedSpeaker}
            onSelectSpeaker={setSelectedSpeaker}
          />
        </div>
      </div>

      <AudioPlayer
        audioUrl={audioUrl}
        metrics={metrics}
        title={t('generatedAudio')}
      />
    </div>
  );
}
