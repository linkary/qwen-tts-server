import React, { useEffect, useState } from 'react';
import { StatusIndicator } from '../ui/StatusIndicator';
import { useI18n } from '../../i18n/I18nContext';
import { checkHealth } from '../../services/api';

export function Header() {
  const { language, setLanguage } = useI18n();
  const [serverStatus, setServerStatus] = useState<{
    status: 'online' | 'loading' | 'offline';
    text: string;
  }>({ status: 'loading', text: 'Checking...' });

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setServerStatus({ status: 'online', text: `v${data.version}` });
      })
      .catch(() => {
        setServerStatus({ status: 'offline', text: 'Offline' });
      });
  }, []);

  return (
    <header className="sticky top-0 z-[100] bg-gradient-to-b from-bg-deep to-bg-deep/95 backdrop-blur-xl border-b border-border-subtle py-lg">
      <div className="max-w-[1200px] mx-auto px-lg">
        <div className="flex items-center justify-between gap-lg flex-wrap">
          {/* Logo */}
          <div className="flex items-center gap-md">
            <div className="w-12 h-12 flex items-center justify-center bg-gradient-to-br from-accent-cyan to-accent-coral rounded-md font-display font-bold text-xl text-bg-deep">
              Q3
            </div>
            <div>
              <div className="font-display text-2xl font-bold bg-gradient-to-r from-accent-cyan to-text-primary bg-clip-text text-transparent">
                Qwen3-TTS
              </div>
              <div className="text-xs text-text-muted font-display">
                Voice Laboratory
              </div>
            </div>
          </div>

          {/* Language Switcher */}
          <div className="flex gap-xs p-xs bg-bg-surface border border-border-subtle rounded-md">
            <button
              onClick={() => setLanguage('en')}
              className={`px-sm py-xs font-display text-xs font-medium rounded transition-all ${
                language === 'en'
                  ? 'text-accent-cyan bg-bg-card'
                  : 'text-text-muted hover:text-text-primary hover:bg-bg-elevated'
              }`}
            >
              EN
            </button>
            <button
              onClick={() => setLanguage('zh-cn')}
              className={`px-sm py-xs font-display text-xs font-medium rounded transition-all ${
                language === 'zh-cn'
                  ? 'text-accent-cyan bg-bg-card'
                  : 'text-text-muted hover:text-text-primary hover:bg-bg-elevated'
              }`}
            >
              中文
            </button>
          </div>

          {/* Status */}
          <StatusIndicator status={serverStatus.status} text={serverStatus.text} />
        </div>
      </div>
    </header>
  );
}
