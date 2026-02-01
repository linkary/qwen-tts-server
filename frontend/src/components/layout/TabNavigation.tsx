import React, { useState } from 'react';
import { cn } from '../../utils/cn';
import { useTranslation } from '../../i18n/I18nContext';

export type TabId = 'custom-voice' | 'voice-design' | 'voice-clone' | 'settings';

interface TabNavigationProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  const t = useTranslation();

  const tabs: { id: TabId; label: string }[] = [
    { id: 'custom-voice', label: t('customVoice') },
    { id: 'voice-design', label: t('voiceDesign') },
    { id: 'voice-clone', label: t('voiceClone') },
    { id: 'settings', label: t('settings') },
  ];

  return (
    <nav
      className="flex gap-xs py-md border-b border-border-subtle mb-xl overflow-x-auto"
      role="tablist"
    >
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={activeTab === tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            'font-display text-sm font-medium px-lg py-sm rounded-md border transition-all whitespace-nowrap',
            activeTab === tab.id
              ? 'text-accent-cyan bg-bg-surface border-accent-cyan shadow-glow-cyan'
              : 'text-text-secondary bg-transparent border-transparent hover:text-text-primary hover:bg-bg-surface'
          )}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
