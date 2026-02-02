import React from 'react';

import { useTranslation } from '../../../i18n/I18nContext';

interface ExamplePrompt {
  i18nKey: string;
  instruct: string;
}

const EXAMPLE_PROMPTS: ExamplePrompt[] = [
  { i18nKey: 'promptBritishWoman', instruct: 'A warm, professional female voice with a slight British accent, speaking confidently and clearly' },
  { i18nKey: 'promptRadioHost', instruct: 'Deep male voice, calm and soothing, like a late-night radio host' },
  { i18nKey: 'promptYoungMan', instruct: 'Young energetic male voice, 20-25 years old, speaking with excitement' },
  { i18nKey: 'promptGrandmother', instruct: 'Elderly wise grandmother voice, gentle and storytelling' },
  { i18nKey: 'promptAIAssistant', instruct: 'Robotic AI assistant voice, clear and precise' },
  { i18nKey: 'promptAnime', instruct: 'Cheerful anime girl voice, high-pitched and cute' },
];

interface ExamplePromptsProps {
  onSelect: (instruct: string) => void;
}

export function ExamplePrompts({ onSelect }: ExamplePromptsProps) {
  const t = useTranslation();

  return (
    <div className="flex flex-wrap gap-sm mb-lg">
      {EXAMPLE_PROMPTS.map((prompt) => {
         // @ts-ignore
         const value = t(`${prompt.i18nKey}Value`);
         return (
        <button
          // @ts-ignore
          key={prompt.i18nKey}
          type="button"
          onClick={() => onSelect(value)}
          className="px-md py-sm bg-bg-surface border border-border-subtle rounded-lg text-xs text-text-secondary cursor-pointer transition-all hover:border-accent-coral hover:text-accent-coral"
        >
          {/* @ts-ignore */}
          {t(prompt.i18nKey)}
        </button>
      )})}
    </div>
  );
}
