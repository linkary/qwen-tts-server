import React, { useRef, useState, useEffect, useCallback } from 'react';
import { AudioWaveform } from './AudioWaveform';
import { PerformanceMetrics } from './PerformanceMetrics';
import { cn } from '../../utils/cn';
import type { AudioMetrics } from '../../types/audio';

interface AudioPlayerProps {
  audioUrl: string | null;
  metrics?: AudioMetrics;
  title?: string;
  showCache?: boolean;
  onLoad?: () => void;
}

function formatTime(seconds: number): string {
  if (!isFinite(seconds) || seconds < 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export function AudioPlayer({ audioUrl, metrics = {}, title = 'Generated Audio', showCache = false, onLoad }: AudioPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  // Auto-play when audioUrl changes
  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play().catch(() => {});
      onLoad?.();
    }
  }, [audioUrl, onLoad]);

  // Audio event handlers
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      if (!isDragging) setCurrentTime(audio.currentTime);
    };
    const handleLoadedMetadata = () => setDuration(audio.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [isDragging]);

  const togglePlayPause = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      audio.play().catch(() => {});
    } else {
      audio.pause();
    }
  }, []);

  const handleSeek = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    const bar = progressRef.current;
    if (!audio || !bar) return;

    const rect = bar.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const newTime = ratio * audio.duration;
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    setIsDragging(true);
    handleSeek(e);

    const handleMouseMove = (ev: MouseEvent) => {
      const audio = audioRef.current;
      const bar = progressRef.current;
      if (!audio || !bar) return;
      const rect = bar.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (ev.clientX - rect.left) / rect.width));
      const newTime = ratio * audio.duration;
      audio.currentTime = newTime;
      setCurrentTime(newTime);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  }, [handleSeek]);

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  if (!audioUrl) return null;

  return (
    <div className="mt-xl p-lg bg-bg-surface border border-border-subtle rounded-lg animate-slideUp">
      <div className="flex items-center justify-between mb-md">
        <span className="font-display text-sm font-semibold text-accent-cyan">{title}</span>
      </div>

      <AudioWaveform
        mode="playback"
        audioElement={audioRef.current}
        isActive={isPlaying}
      />

      {/* Custom Audio Controls */}
      <div className="flex items-center gap-md mt-md">
        {/* Play/Pause Button */}
        <button
          onClick={togglePlayPause}
          className="flex-shrink-0 w-10 h-10 rounded-full bg-accent-cyan text-bg-deep flex items-center justify-center hover:shadow-glow-cyan transition-all duration-150 hover:scale-105 active:scale-95"
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <rect x="3" y="2" width="4" height="12" rx="1" />
              <rect x="9" y="2" width="4" height="12" rx="1" />
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M4 2.5a.5.5 0 0 1 .764-.424l9 5.5a.5.5 0 0 1 0 .848l-9 5.5A.5.5 0 0 1 4 13.5V2.5z" />
            </svg>
          )}
        </button>

        {/* Current Time */}
        <span className="font-display text-xs text-text-secondary tabular-nums w-10 text-right">
          {formatTime(currentTime)}
        </span>

        {/* Progress Bar */}
        <div
          ref={progressRef}
          className="flex-1 h-8 flex items-center cursor-pointer group"
          onMouseDown={handleMouseDown}
        >
          <div className="w-full h-1.5 bg-bg-elevated rounded-full relative overflow-visible">
            {/* Progress Fill */}
            <div
              className="absolute top-0 left-0 h-full bg-gradient-to-r from-accent-cyan to-accent-cyan-dim rounded-full transition-[width] duration-75"
              style={{ width: `${progress}%` }}
            />
            {/* Seek Handle */}
            <div
              className={cn(
                'absolute top-1/2 -translate-y-1/2 w-3.5 h-3.5 bg-accent-cyan rounded-full shadow-glow-cyan transition-all duration-75',
                'opacity-0 group-hover:opacity-100',
                isDragging && 'opacity-100 scale-125'
              )}
              style={{ left: `calc(${progress}% - 7px)` }}
            />
          </div>
        </div>

        {/* Duration */}
        <span className="font-display text-xs text-text-secondary tabular-nums w-10">
          {formatTime(duration)}
        </span>
      </div>

      {/* Hidden audio element */}
      <audio ref={audioRef} preload="metadata" />

      <PerformanceMetrics metrics={metrics} showCache={showCache} />
    </div>
  );
}
