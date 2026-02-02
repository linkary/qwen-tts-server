import React, { useState } from 'react';
import { Card } from '../../ui/Card';
import { FormTextarea } from '../../forms/FormTextarea';
import { FormSelect } from '../../forms/FormSelect';
import { RangeSlider } from '../../forms/RangeSlider';
import { Button } from '../../ui/Button';
import { AudioPlayer } from '../../audio/AudioPlayer';
import { ExamplePrompts } from './ExamplePrompts';
import { useAppContext } from '../../../context/AppContext';
import { useToast } from '../../../context/ToastContext';
import { useTranslation } from '../../../i18n/I18nContext';
import { generateVoiceDesign } from '../../../services/api';
import { base64ToBlob } from '../../../utils/audio';
import type { AudioMetrics } from '../../../types/audio';

export function VoiceDesignTab() {
  const t = useTranslation();
  const { apiKey } = useAppContext();
  const { showToast } = useToast();

  const [instruct, setInstruct] = useState(t('defaultInstructVoiceDesign'));
  const [text, setText] = useState(t('defaultTextVoiceDesign'));
  const [language, setLanguage] = useState('English');
  const [speed, setSpeed] = useState(1.0);
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<AudioMetrics>({});

  const handleGenerate = async () => {
    if (!text.trim()) {
      showToast(t('noText'), 'warning');
      return;
    }

    if (!instruct.trim()) {
      showToast(t('noVoiceDesc'), 'warning');
      return;
    }

    if (!apiKey) {
      showToast(t('noApiKey'), 'warning');
      return;
    }

    setIsLoading(true);
    const startTime = performance.now();

    try {
      const { data, headers } = await generateVoiceDesign(
        {
          text,
          language,
          instruct,
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
        <h1 className="text-2xl mb-sm text-text-primary">{t('vdTitle')}</h1>
        <p className="text-text-secondary text-base max-w-[600px]">{t('vdDesc')}</p>
      </div>

      <Card>
        <div className="mb-lg">
          <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
            {t('examplePrompts')}
          </label>
          <ExamplePrompts onSelect={setInstruct} />
        </div>

        <FormTextarea
          label={t('voiceDescription')}
          value={instruct}
          onChange={(e) => setInstruct(e.target.value)}
          placeholder={t('voiceDescPlaceholder')}
          maxLength={1000}
        />

        <FormTextarea
          label={t('textToSynth')}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t('textPlaceholder')}
          maxLength={1000}
        />

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
          <span>▶</span> {t('btnGenerateVoiceDesign')}
        </Button>
      </Card>

      <AudioPlayer audioUrl={audioUrl} metrics={metrics} title={t('generatedAudio')} />
    </div>
  );
}
