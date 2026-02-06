import React, { useState } from 'react';
import { AudioWaveform } from '../../audio/AudioWaveform';
import { Mic, Square } from 'lucide-react';
import { Button } from '../../ui/Button';
import { useTranslation } from '../../../i18n/I18nContext';
import { useAudioRecorder } from '../../../hooks/useAudioRecorder';
import { useToast } from '../../../context/ToastContext';
import { fileToBase64 } from '../../../utils/audio';
import { formatFileSize } from '../../../utils/format';
import animationStyles from '../../../styles/animations.module.css';
import { RECORDING_PROMPTS } from '../../../config/recordingPrompts';
import { useI18n } from '../../../i18n/I18nContext';

interface AudioRecorderProps {
  onAudioRecorded: (base64: string, blob: Blob) => void;
}

export function AudioRecorder({ onAudioRecorded }: AudioRecorderProps) {
  const t = useTranslation();
  const { language } = useI18n();
  const { showToast } = useToast();
  const { isRecording, recordingTime, audioBlob, audioUrl, startRecording, stopRecording, error, mediaStream } =
    useAudioRecorder();
  const [hasRecorded, setHasRecorded] = useState(false);
  const [isStarting, setIsStarting] = useState(false);

  const handleStart = async () => {
    setIsStarting(true);
    await startRecording();
    setIsStarting(false);
    if (error) {
      showToast(t('microphoneError'), 'error');
    } else {
      showToast(t('recordingStarted'), 'info');
    }
  };

  const handleStop = async () => {
    stopRecording();
    setHasRecorded(true);
    showToast(t('recordingComplete'), 'success');
    
    if (audioBlob) {
      const file = new File([audioBlob], 'recording.webm', { type: 'audio/webm' });
      const base64 = await fileToBase64(file);
      onAudioRecorded(base64, audioBlob);
    }
  };

  const mins = Math.floor(recordingTime / 60);
  const secs = recordingTime % 60;
  const timeDisplay = `${mins}:${secs.toString().padStart(2, '0')}`;

  const promptText = RECORDING_PROMPTS[language] || RECORDING_PROMPTS.en;

  return (
    <div>
      {/* Recording Prompt */}
      <div className="mb-lg p-lg bg-gradient-to-br from-[rgba(0,245,212,0.08)] to-[rgba(255,107,107,0.05)] border border-accent-cyan rounded-lg">
        <div className="font-display text-xs font-semibold text-accent-cyan uppercase tracking-widest mb-sm">
          {t('readAloud')}
        </div>
        <div className="text-lg leading-relaxed text-text-primary p-md bg-bg-card rounded-md mb-sm border-l-[3px] border-accent-cyan">
          {promptText}
        </div>
        <div className="text-xs text-text-muted italic">{t('recordingTip')}</div>
      </div>

      {/* Recording Controls */}
      <div className="mb-lg">
        <div className="flex gap-md mb-md">
          {!isRecording ? (
            <Button
              variant="danger"
              onClick={handleStart}
              isLoading={isStarting}
              className="flex-1 bg-gradient-to-br from-accent-coral to-accent-coral-dim text-bg-deep font-semibold"
            >
              <Mic className="w-4 h-4" />
              <span>{t('startRecording')}</span>
            </Button>
          ) : (
            <Button
              variant="secondary"
              onClick={handleStop}
              className="flex-1 border-2 border-accent-coral text-accent-coral hover:bg-[rgba(255,107,107,0.1)]"
            >
              <Square className="w-4 h-4 fill-current" />
              <span>{t('stopRecording')}</span>
            </Button>
          )}
        </div>

        {isRecording && (
          <div className="mb-md">
            <AudioWaveform 
              mode="recording" 
              mediaStream={mediaStream} 
              isActive={isRecording}
              className="mb-sm border border-accent-coral/30"
              barColor="#ff6b6b" // accent-coral
            />
            <div className="flex items-center justify-center gap-sm text-accent-coral font-display text-sm">
              <div className={animationStyles['recording-dot']} />
              <span>{t('recording')}</span>
              <span>{timeDisplay}</span>
            </div>
          </div>
        )}
      </div>

      {/* Recording Preview */}
      {hasRecorded && audioBlob && audioUrl && (
        <div className="p-lg bg-bg-surface border border-border-subtle rounded-md">
          <div className="flex items-center justify-between mb-md">
            <span className="font-display text-sm text-text-primary">{t('recordedAudio')}</span>
            <span className="text-xs text-text-muted">{formatFileSize(audioBlob.size)}</span>
          </div>
          <audio controls src={audioUrl} className="w-full" />
        </div>
      )}
    </div>
  );
}
