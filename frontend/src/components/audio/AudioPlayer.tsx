import React, { useRef, useEffect } from 'react';
import { WaveformVisualizer } from './WaveformVisualizer';
import { PerformanceMetrics } from './PerformanceMetrics';
import type { AudioMetrics } from '../../types/audio';

interface AudioPlayerProps {
  audioUrl: string | null;
  metrics?: AudioMetrics;
  title?: string;
  showCache?: boolean;
  onLoad?: () => void;
}

export function AudioPlayer({ audioUrl, metrics = {}, title = 'Generated Audio', showCache = false, onLoad }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play().catch(() => {});
      onLoad?.();
    }
  }, [audioUrl, onLoad]);

  if (!audioUrl) return null;

  return (
    <div className="mt-xl p-lg bg-bg-surface border border-border-subtle rounded-lg animate-slideUp">
      <div className="flex items-center justify-between mb-md">
        <span className="font-display text-sm font-semibold text-accent-cyan">{title}</span>
      </div>
      
      <WaveformVisualizer audioElement={audioRef.current} />
      
      <audio ref={audioRef} controls className="w-full h-10" />
      
      <PerformanceMetrics metrics={metrics} showCache={showCache} />
    </div>
  );
}
