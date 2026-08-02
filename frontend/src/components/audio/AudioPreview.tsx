import React from 'react';
import { AudioPlayerControls } from './AudioPlayerControls';
import { useAudioPlayback } from '../../hooks/useAudioPlayback';

interface AudioPreviewProps {
  audioUrl: string | null;
  className?: string;
}

/**
 * Playback for a reference clip the user just recorded or picked.
 *
 * No autoplay (the user did not ask to hear it back), no performance metrics (they
 * describe generation, not a source file), no waveform, and no frame of its own --
 * the calling card already owns the padding, border and header row.
 */
export function AudioPreview({ audioUrl, className }: AudioPreviewProps) {
  const playback = useAudioPlayback(audioUrl, { autoPlay: false });

  if (!audioUrl) return null;

  return <AudioPlayerControls playback={playback} size="sm" className={className} />;
}
