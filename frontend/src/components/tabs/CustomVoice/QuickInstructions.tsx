import React from 'react';
import { Smile, Coffee, PartyPopper, Glasses, Flower2, LucideIcon } from 'lucide-react';
import { useTranslation } from '../../../i18n/I18nContext';

interface QuickInstruction {
  i18nKey: string;
  value: string;
  icon: LucideIcon;
}

const QUICK_INSTRUCTIONS: Omit<QuickInstruction, 'label'>[] = [
  { i18nKey: 'presetHappy', value: 'Speak happily and with energy', icon: Smile },
  { i18nKey: 'presetCalm', value: 'Speak in a calm, soothing manner', icon: Coffee },
  { i18nKey: 'presetExcited', value: 'Speak with excitement and enthusiasm', icon: PartyPopper },
  { i18nKey: 'presetSerious', value: 'Speak in a serious, professional tone', icon: Glasses },
  { i18nKey: 'presetSoft', value: 'Speak softly and gently', icon: Flower2 },
];

interface QuickInstructionsProps {
  onSelect: (value: string) => void;
}

export function QuickInstructions({ onSelect }: QuickInstructionsProps) {
  const t = useTranslation();
  
  return (
    <div className="flex flex-wrap gap-sm mt-sm">
      {QUICK_INSTRUCTIONS.map((instruction) => {
        const Icon = instruction.icon;
        // @ts-ignore
        const label = t(instruction.i18nKey);
         // @ts-ignore
        const value = t(`${instruction.i18nKey}Value`);
        return (
          <button
            key={instruction.value}
            type="button"
            onClick={() => onSelect(value)}
            className="flex items-center gap-xs px-md py-xs bg-bg-surface border border-border-subtle rounded-lg text-xs text-text-secondary cursor-pointer transition-all hover:border-accent-cyan hover:text-accent-cyan group"
          >
            <Icon className="w-3.5 h-3.5 group-hover:text-accent-cyan transition-colors" />
            {label}
          </button>
        );
      })}
    </div>
  );
}
