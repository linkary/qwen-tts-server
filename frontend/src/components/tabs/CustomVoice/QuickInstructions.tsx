import React from 'react';
import { Smile, Coffee, PartyPopper, Glasses, Flower2, LucideIcon } from 'lucide-react';

interface QuickInstruction {
  label: string;
  value: string;
  icon: LucideIcon;
}

const QUICK_INSTRUCTIONS: QuickInstruction[] = [
  { label: 'Happy', value: 'Speak happily and with energy', icon: Smile },
  { label: 'Calm', value: 'Speak in a calm, soothing manner', icon: Coffee },
  { label: 'Excited', value: 'Speak with excitement and enthusiasm', icon: PartyPopper },
  { label: 'Serious', value: 'Speak in a serious, professional tone', icon: Glasses },
  { label: 'Soft', value: 'Speak softly and gently', icon: Flower2 },
];

interface QuickInstructionsProps {
  onSelect: (value: string) => void;
}

export function QuickInstructions({ onSelect }: QuickInstructionsProps) {
  return (
    <div className="flex flex-wrap gap-sm mt-sm">
      {QUICK_INSTRUCTIONS.map((instruction) => {
        const Icon = instruction.icon;
        return (
          <button
            key={instruction.value}
            type="button"
            onClick={() => onSelect(instruction.value)}
            className="flex items-center gap-xs px-md py-xs bg-bg-surface border border-border-subtle rounded-lg text-xs text-text-secondary cursor-pointer transition-all hover:border-accent-cyan hover:text-accent-cyan group"
          >
            <Icon className="w-3.5 h-3.5 group-hover:text-accent-cyan transition-colors" />
            {instruction.label}
          </button>
        );
      })}
    </div>
  );
}
