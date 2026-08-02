import React from 'react';
import { AudioWaveform } from './AudioWaveform';
import { AudioPlayerControls } from './AudioPlayerControls';
import { PerformanceMetrics } from './PerformanceMetrics';
import { useAudioPlayback } from '../../hooks/useAudioPlayback';
import type { AudioMetrics } from '../../types/audio';

interface AudioPlayerProps {
  audioUrl: string | null;
  metrics?: AudioMetrics;
  title?: string;
  showCache?: boolean;
  onLoad?: () => void;
}

export function AudioPlayer({ audioUrl, metrics = {}, title = 'Generated Audio', showCache = false, onLoad }: AudioPlayerProps) {
  const playback = useAudioPlayback(audioUrl, { autoPlay: true, onLoad });

  if (!audioUrl) return null;

  return (
    <div className="mt-xl p-lg bg-bg-surface border border-border-subtle rounded-lg animate-slideUp">
      <div className="flex items-center justify-between mb-md">
        <span className="font-display text-sm font-semibold text-accent-cyan">{title}</span>
      </div>

      <AudioWaveform
        mode="playback"
        audioElement={playback.audioRef.current}
        isActive={playback.isPlaying}
      />

      <AudioPlayerControls playback={playback} className="mt-md" />

      <PerformanceMetrics metrics={metrics} showCache={showCache} />
    </div>
  );
}
