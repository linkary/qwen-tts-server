import React from 'react';
import { BookOpen, Book, Clipboard, FileJson } from 'lucide-react';
import { ApiKeyConfig } from './ApiKeyConfig';
import { ServerStatus } from './ServerStatus';
import { CacheStats } from './CacheStats';
import { useTranslation } from '../../../i18n/I18nContext';

export function SettingsTab() {
  const t = useTranslation();

  return (
    <div>
      <div className="mb-xl">
        <h1 className="text-2xl mb-sm text-text-primary">{t('settingsTitle')}</h1>
        <p className="text-text-secondary text-base max-w-[600px]">{t('settingsDesc')}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
        <ApiKeyConfig />
        <ServerStatus />
        <CacheStats />
        
        {/* API Documentation Card */}
        <div className="p-lg bg-bg-surface border border-border-subtle rounded-lg">
          <h3 className="font-display text-sm font-semibold text-text-primary mb-md flex items-center gap-sm">
            <BookOpen className="w-4 h-4" /> {t('apiDocs')}
          </h3>
          <p className="text-sm text-text-secondary mb-md">
            Access the full API documentation and interactive testing tools.
          </p>
          <div className="flex flex-col gap-sm">
            <a
              href="/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center px-xl py-md font-display text-sm font-semibold uppercase tracking-wider rounded-md bg-bg-surface text-text-primary border border-border-subtle hover:bg-bg-elevated hover:border-border-active transition-all no-underline"
            >
              <div className="flex items-center justify-center gap-sm">
                <Book className="w-4 h-4" /> Swagger UI
              </div>
            </a>
            <a
              href="/redoc"
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center px-xl py-md font-display text-sm font-semibold uppercase tracking-wider rounded-md bg-bg-surface text-text-primary border border-border-subtle hover:bg-bg-elevated hover:border-border-active transition-all no-underline"
            >
              <div className="flex items-center justify-center gap-sm">
                <Clipboard className="w-4 h-4" /> ReDoc
              </div>
            </a>
            <a
              href="/openapi.json"
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center px-xl py-md font-display text-sm font-semibold uppercase tracking-wider rounded-md bg-bg-surface text-text-primary border border-border-subtle hover:bg-bg-elevated hover:border-border-active transition-all no-underline"
            >
              <div className="flex items-center justify-center gap-sm">
                <FileJson className="w-4 h-4" /> OpenAPI JSON
              </div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
