import React from 'react';
import { X } from 'lucide-react';
import type { VoicePrompt } from '../../../types';
import { useTranslation } from '../../../i18n/I18nContext';

interface SavedPromptsProps {
  prompts: VoicePrompt[];
  selectedPromptId: string | null;
  onSelectPrompt: (id: string) => void;
  onDeletePrompt: (id: string) => void;
}

export function SavedPrompts({
  prompts,
  selectedPromptId,
  onSelectPrompt,
  onDeletePrompt,
}: SavedPromptsProps) {
  const t = useTranslation();

  if (prompts.length === 0) {
    return (
      <div className="mt-lg">
        <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
          {t('savedPrompts')}
        </label>
        <p className="text-text-muted text-sm">No saved prompts yet</p>
      </div>
    );
  }

  return (
    <div className="mt-lg">
      <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
        {t('savedPrompts')}
      </label>
      <div>
        {prompts.map((prompt) => (
          <div
            key={prompt.id}
            onClick={() => onSelectPrompt(prompt.id)}
            className={`flex items-center justify-between p-md bg-bg-surface border rounded-md mb-sm cursor-pointer transition-all ${
              selectedPromptId === prompt.id
                ? 'border-accent-cyan'
                : 'border-border-subtle hover:border-border-active'
            }`}
          >
            <div>
              <div className="font-display text-xs text-text-muted">
                ID: {prompt.id.slice(0, 8)}...
              </div>
              <div className="text-[0.625rem] text-text-muted">
                {new Date(prompt.createdAt).toLocaleDateString()}
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDeletePrompt(prompt.id);
              }}
              className="text-text-muted hover:text-accent-coral p-xs"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
