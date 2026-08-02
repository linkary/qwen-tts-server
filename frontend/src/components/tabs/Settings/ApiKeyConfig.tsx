import React, { useState } from 'react';
import { Key, Eye, EyeOff, Download } from 'lucide-react';
import { Button } from '../../ui/Button';
import { useAppContext } from '../../../context/AppContext';
import { useToast } from '../../../context/ToastContext';
import { useTranslation } from '../../../i18n/I18nContext';
import { fetchDevApiKey } from '../../../services/api';

export function ApiKeyConfig() {
  const t = useTranslation();
  const { apiKey, setApiKey } = useAppContext();
  const { showToast } = useToast();
  const [localKey, setLocalKey] = useState(apiKey);
  const [showKey, setShowKey] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  // The endpoint only exists when the server ran with EXPOSE_API_KEY=true. Discovering
  // that on the first click costs nothing, where advertising it from /health would mean
  // adding a field to a public endpoint.
  const [canFetch, setCanFetch] = useState(true);

  const handleSave = () => {
    setApiKey(localKey.trim());
    showToast(t('apiKeySaved'), 'success');
  };

  const handleFetch = async () => {
    setIsFetching(true);
    try {
      const result = await fetchDevApiKey();
      if (!result) {
        setCanFetch(false);
        showToast(t('apiKeyFetchUnavailable'), 'info');
      } else if (!result.auth_required || !result.api_key) {
        // Deliberately leaves the field alone: every generate path refuses to run on an
        // empty key, so clearing it here would break the tabs this button is meant to help.
        showToast(t('apiKeyAuthDisabled'), 'info');
      } else {
        // Commits straight away rather than staging a draft for Save -- one click, one
        // intent, and no "I fetched it but generation still says no API key".
        setLocalKey(result.api_key);
        setApiKey(result.api_key);
        showToast(t('apiKeyFetched'), 'success');
      }
    } catch (error) {
      console.error('Failed to fetch API key:', error);
      showToast(t('apiKeyFetchFailed'), 'error');
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <div className="p-lg bg-bg-surface border border-border-subtle rounded-lg">
      <h3 className="font-display text-sm font-semibold text-text-primary mb-md flex items-center gap-sm">
        <Key className="w-4 h-4 text-accent-cyan" /> {t('apiKey')}
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
            placeholder={t('apiKeyPlaceholder')}
            className="w-full pr-12 px-md py-md font-body text-base text-text-primary bg-bg-surface border border-border-subtle rounded-md focus:outline-none focus:border-accent-cyan focus:shadow-[0_0_0_3px_rgba(0,245,212,0.1)]"
          />
          <button
            onClick={() => setShowKey(!showKey)}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted hover:text-text-primary p-xs"
            title={t('showHideApiKey')}
          >
            {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
          </button>
        </div>
        <p className="text-xs text-text-muted mt-sm">{t('apiKeyHint')}</p>
      </div>
      <div className="flex gap-md">
        <Button variant="secondary" onClick={handleSave} className="flex-1">
          {t('saveApiKey')}
        </Button>
        {canFetch && (
          <Button
            variant="secondary"
            onClick={handleFetch}
            isLoading={isFetching}
            loadingText={t('apiKeyFetching')}
          >
            <Download className="w-4 h-4" />
            <span>{t('fetchApiKey')}</span>
          </Button>
        )}
      </div>
    </div>
  );
}
