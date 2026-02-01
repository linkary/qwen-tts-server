import React, { useState } from 'react';
import { FormInput } from '../../forms/FormInput';
import { Button } from '../../ui/Button';
import { useAppContext } from '../../../context/AppContext';
import { useToast } from '../../../context/ToastContext';
import { useTranslation } from '../../../i18n/I18nContext';

export function ApiKeyConfig() {
  const t = useTranslation();
  const { apiKey, setApiKey } = useAppContext();
  const { showToast } = useToast();
  const [localKey, setLocalKey] = useState(apiKey);
  const [showKey, setShowKey] = useState(false);

  const handleSave = () => {
    setApiKey(localKey.trim());
    showToast(t('apiKeySaved'), 'success');
  };

  return (
    <div className="p-lg bg-bg-surface border border-border-subtle rounded-lg">
      <h3 className="font-display text-sm font-semibold text-text-primary mb-md flex items-center gap-sm">
        🔑 {t('apiKey')}
      </h3>
      <div className="mb-md">
        <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
          {t('apiKey')}
        </label>
        <div className="relative">
          <input
            type={showKey ? 'text' : 'password'}
            value={localKey}
            onChange={(e) => setLocalKey(e.target.value)}
            placeholder="Enter your API key..."
            className="w-full pr-12 px-md py-md font-body text-base text-text-primary bg-bg-surface border border-border-subtle rounded-md focus:outline-none focus:border-accent-cyan focus:shadow-[0_0_0_3px_rgba(0,245,212,0.1)]"
          />
          <button
            onClick={() => setShowKey(!showKey)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary p-xs"
            title="Show/Hide"
          >
            {showKey ? '🙈' : '👁️'}
          </button>
        </div>
        <p className="text-xs text-text-muted mt-sm">
          Required for all API requests. Stored locally in your browser.
        </p>
      </div>
      <Button variant="secondary" onClick={handleSave} className="w-full">
        {t('saveApiKey')}
      </Button>
    </div>
  );
}
