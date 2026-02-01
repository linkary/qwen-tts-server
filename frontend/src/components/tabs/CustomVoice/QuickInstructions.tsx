import React from 'react';

interface QuickInstruction {
  label: string;
  value: string;
}

const QUICK_INSTRUCTIONS: QuickInstruction[] = [
  { label: 'Happy 😊', value: 'Speak happily and with energy' },
  { label: 'Calm 😌', value: 'Speak in a calm, soothing manner' },
  { label: 'Excited 🎉', value: 'Speak with excitement and enthusiasm' },
  { label: 'Serious 🧐', value: 'Speak in a serious, professional tone' },
  { label: 'Soft 🌸', value: 'Speak softly and gently' },
];

interface QuickInstructionsProps {
  onSelect: (value: string) => void;
}

export function QuickInstructions({ onSelect }: QuickInstructionsProps) {
  return (
    <div className="flex flex-wrap gap-sm mt-sm">
      {QUICK_INSTRUCTIONS.map((instruction) => (
        <button
          key={instruction.value}
          type="button"
          onClick={() => onSelect(instruction.value)}
          className="px-md py-xs bg-bg-surface border border-border-subtle rounded-lg text-xs text-text-secondary cursor-pointer transition-all hover:border-accent-cyan hover:text-accent-cyan"
        >
          {instruction.label}
        </button>
      ))}
    </div>
  );
}
