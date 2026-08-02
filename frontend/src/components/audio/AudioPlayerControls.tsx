import React from 'react';
import { cn } from '../../utils/cn';
import type { UseAudioPlaybackReturn } from '../../hooks/useAudioPlayback';

interface AudioPlayerControlsProps {
  playback: UseAudioPlaybackReturn;
  size?: 'sm' | 'md';
  className?: string;
}

const sizeStyles = {
  sm: { row: 'gap-sm', button: 'w-8 h-8', icon: 14, time: 'w-8' },
  md: { row: 'gap-md', button: 'w-10 h-10', icon: 16, time: 'w-10' },
} as const;

function formatTime(seconds: number): string {
  if (!isFinite(seconds) || seconds < 0) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Play/pause button, mm:ss readouts and a draggable seek bar for a useAudioPlayback
 * instance, plus the <audio> element the hook drives.
 *
 * The element sits outside the flex row on purpose: CSS gap applies between every
 * flex child including a zero-size one, so making it a sibling of the controls would
 * add a phantom gap after the duration label.
 */
export function AudioPlayerControls({ playback, size = 'md', className }: AudioPlayerControlsProps) {
  // Destructured up front, not read as playback.x inside the JSX: the react-hooks/refs
  // rule cannot tell a forwarded ref object from a read of its .current and flags every
  // property access on an object that carries refs.
  const {
    audioRef,
    progressRef,
    isPlaying,
    currentTime,
    duration,
    isDragging,
    progress,
    togglePlayPause,
    handleMouseDown,
  } = playback;
  const s = sizeStyles[size];

  return (
    <>
      <div className={cn('flex items-center', s.row, className)}>
        {/* Play/Pause Button */}
        <button
          onClick={togglePlayPause}
          className={cn(
            'flex-shrink-0 rounded-full bg-accent-cyan text-bg-deep flex items-center justify-center',
            'hover:shadow-glow-cyan transition-all duration-150 hover:scale-105 active:scale-95',
            s.button
          )}
          aria-label={isPlaying ? 'Pause' : 'Play'}
        >
          {isPlaying ? (
            <svg width={s.icon} height={s.icon} viewBox="0 0 16 16" fill="currentColor">
              <rect x="3" y="2" width="4" height="12" rx="1" />
              <rect x="9" y="2" width="4" height="12" rx="1" />
            </svg>
          ) : (
            <svg width={s.icon} height={s.icon} viewBox="0 0 16 16" fill="currentColor">
              <path d="M4 2.5a.5.5 0 0 1 .764-.424l9 5.5a.5.5 0 0 1 0 .848l-9 5.5A.5.5 0 0 1 4 13.5V2.5z" />
            </svg>
          )}
        </button>

        {/* Current Time */}
        <span
          className={cn('font-display text-xs text-text-secondary tabular-nums text-right', s.time)}
        >
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
        <span className={cn('font-display text-xs text-text-secondary tabular-nums', s.time)}>
          {formatTime(duration)}
        </span>
      </div>

      <audio ref={audioRef} preload="metadata" />
    </>
  );
}
