import React, { useState, useRef, useEffect, useCallback } from 'react';

export interface AudioPlaybackOptions {
  /** Start playing as soon as audioUrl changes. True for generated output, false for previews. */
  autoPlay?: boolean;
  onLoad?: () => void;
}

export interface UseAudioPlaybackReturn {
  /** Attach to the <audio> element that this hook drives. */
  audioRef: React.RefObject<HTMLAudioElement | null>;
  /** Attach to the seek bar track that handleMouseDown measures against. */
  progressRef: React.RefObject<HTMLDivElement | null>;
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  isDragging: boolean;
  /** Played fraction as a percentage (0-100), derived from currentTime/duration. */
  progress: number;
  togglePlayPause: () => void;
  handleMouseDown: (e: React.MouseEvent<HTMLDivElement>) => void;
}

/**
 * Drives an <audio> element: play/pause, seeking, and time/duration readouts.
 *
 * The caller owns the markup, so the same logic backs both the full generated-audio
 * player and the compact reference-clip preview.
 */
export function useAudioPlayback(
  audioUrl: string | null,
  options: AudioPlaybackOptions = {}
): UseAudioPlaybackReturn {
  const { autoPlay = false, onLoad } = options;

  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  // Side effect, deliberate: onLoad is held in a ref so it stays out of the effect
  // below's dependencies. Passing an inline arrow would otherwise re-run that effect
  // on every render, reassigning src and restarting playback mid-listen.
  const onLoadRef = useRef(onLoad);
  useEffect(() => {
    onLoadRef.current = onLoad;
  }, [onLoad]);

  // Load the source, and play it if the caller asked for autoplay
  useEffect(() => {
    const audio = audioRef.current;
    if (!audioUrl || !audio) return;

    audio.src = audioUrl;
    if (autoPlay) {
      audio.play().catch(() => {});
    }
    onLoadRef.current?.();
  }, [audioUrl, autoPlay]);

  // Mirror the element's state into React state.
  //
  // audioUrl is a dependency because consumers render the <audio> element only once they
  // have a URL (AudioPlayer returns null before then). Keyed on isDragging alone, this
  // effect would run once against a null ref, attach nothing, and never re-run -- leaving
  // the time readouts and seek bar frozen at 0:00 for the whole session.
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleTimeUpdate = () => {
      if (!isDragging) setCurrentTime(audio.currentTime);
    };
    const handleLoadedMetadata = () => setDuration(audio.duration);
    const handleDurationChange = () => setDuration(audio.duration);
    const handlePlay = () => setIsPlaying(true);
    const handlePause = () => setIsPlaying(false);
    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('durationchange', handleDurationChange);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);

    // Metadata may already have arrived before this effect ran, in which case the events
    // above have fired and will not fire again. Seed from the element instead of waiting.
    if (audio.readyState >= 1) {
      setDuration(audio.duration);
      setCurrentTime(audio.currentTime);
      setIsPlaying(!audio.paused);
    }

    return () => {
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('durationchange', handleDurationChange);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
    };
  }, [isDragging, audioUrl]);

  const togglePlayPause = useCallback(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (audio.paused) {
      audio.play().catch(() => {});
    } else {
      audio.pause();
    }
  }, []);

  const seekToClientX = useCallback((clientX: number) => {
    const audio = audioRef.current;
    const bar = progressRef.current;
    if (!audio || !bar) return;

    const rect = bar.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
    const newTime = ratio * audio.duration;
    if (!isFinite(newTime)) return;

    audio.currentTime = newTime;
    setCurrentTime(newTime);
  }, []);

  const handleMouseDown = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      setIsDragging(true);
      seekToClientX(e.clientX);

      const handleMouseMove = (ev: MouseEvent) => seekToClientX(ev.clientX);
      const handleMouseUp = () => {
        setIsDragging(false);
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };

      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    },
    [seekToClientX]
  );

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return {
    audioRef,
    progressRef,
    isPlaying,
    currentTime,
    duration,
    isDragging,
    progress,
    togglePlayPause,
    handleMouseDown,
  };
}
