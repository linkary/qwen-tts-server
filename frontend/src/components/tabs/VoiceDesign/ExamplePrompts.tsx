import React from 'react';

interface ExamplePrompt {
  label: string;
  instruct: string;
}

const EXAMPLE_PROMPTS: ExamplePrompt[] = [
  { label: 'Professional British Woman', instruct: 'A warm, professional female voice with a slight British accent, speaking confidently and clearly' },
  { label: 'Radio Host', instruct: 'Deep male voice, calm and soothing, like a late-night radio host' },
  { label: 'Energetic Young Man', instruct: 'Young energetic male voice, 20-25 years old, speaking with excitement' },
  { label: 'Wise Grandmother', instruct: 'Elderly wise grandmother voice, gentle and storytelling' },
  { label: 'AI Assistant', instruct: 'Robotic AI assistant voice, clear and precise' },
  { label: 'Anime Character', instruct: 'Cheerful anime girl voice, high-pitched and cute' },
];

interface ExamplePromptsProps {
  onSelect: (instruct: string) => void;
}

export function ExamplePrompts({ onSelect }: ExamplePromptsProps) {
  return (
    <div className="flex flex-wrap gap-sm mb-lg">
      {EXAMPLE_PROMPTS.map((prompt) => (
        <button
          key={prompt.label}
          type="button"
          onClick={() => onSelect(prompt.instruct)}
          className="px-md py-sm bg-bg-surface border border-border-subtle rounded-lg text-xs text-text-secondary cursor-pointer transition-all hover:border-accent-coral hover:text-accent-coral"
        >
          {prompt.label}
        </button>
      ))}
    </div>
  );
}
