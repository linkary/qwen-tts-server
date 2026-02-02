import React from 'react';
import { SPEAKERS } from '../../../config/speakers';
import { cn } from '../../../utils/cn';
import { useTranslation } from '../../../i18n/I18nContext';

interface SpeakerGridProps {
  selectedSpeaker: string;
  onSelectSpeaker: (speaker: string) => void;
}

export function SpeakerGrid({ selectedSpeaker, onSelectSpeaker }: SpeakerGridProps) {
  const t = useTranslation();
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(160px,1fr))] gap-md mb-lg">
      {SPEAKERS.map((speaker) => (
        <div
          key={speaker.name}
          onClick={() => onSelectSpeaker(speaker.name)}
          className={cn(
            'p-md bg-bg-surface border-2 rounded-md cursor-pointer transition-all text-center',
            selectedSpeaker === speaker.name
              ? 'border-accent-cyan shadow-glow-cyan'
              : 'border-border-subtle hover:border-border-active hover:bg-bg-elevated'
          )}
        >
          <div className="font-display text-sm font-semibold text-text-primary mb-xs">
            {speaker.name.replace('_', ' ')}
          </div>
          <div className="text-xs text-accent-cyan mb-xs">
            {speaker.native_language}
          </div>
          <div className="text-xs text-text-muted leading-snug">
            {/* @ts-ignore */}
            {t(`${speaker.i18nKey}Desc`)}
          </div>
        </div>
      ))}
    </div>
  );
}
