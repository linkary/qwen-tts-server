import React, { useEffect, useState } from 'react';
import { Server } from 'lucide-react';
import { Button } from '../../ui/Button';
import { useAppContext } from '../../../context/AppContext';
import { useTranslation } from '../../../i18n/I18nContext';
import { checkHealth, checkModelsHealth } from '../../../services/api';
import type { ModelsHealthResponse } from '../../../types/api';

export function ServerStatus() {
  const t = useTranslation();
  const [models, setModels] = useState<ModelsHealthResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refresh = async () => {
    setIsRefreshing(true);
    try {
      await checkHealth();
      const data = await checkModelsHealth();
      setModels(data);
    } catch (error) {
      console.error('Failed to check status:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refresh();
  }, []);

  return (
    <div className="p-lg bg-bg-surface border border-border-subtle rounded-lg">
      <h3 className="font-display text-sm font-semibold text-text-primary mb-md flex items-center gap-sm">
        <Server className="w-4 h-4 text-accent-cyan" /> {t('serverStatus')}
      </h3>
      
      <div className="grid grid-cols-3 gap-md mb-md">
        <div className="p-md bg-bg-card rounded-md text-center">
          <div className="text-[0.625rem] font-medium text-text-muted uppercase tracking-widest mb-xs">
            Custom Voice
          </div>
          <div
            className={`font-display text-sm font-semibold ${
              models?.custom_voice_loaded ? 'text-accent-cyan' : 'text-text-muted'
            }`}
          >
            {models ? (models.custom_voice_loaded ? 'Loaded' : 'Not Loaded') : '--'}
          </div>
        </div>

        <div className="p-md bg-bg-card rounded-md text-center">
          <div className="text-[0.625rem] font-medium text-text-muted uppercase tracking-widest mb-xs">
            Voice Design
          </div>
          <div
            className={`font-display text-sm font-semibold ${
              models?.voice_design_loaded ? 'text-accent-cyan' : 'text-text-muted'
            }`}
          >
            {models ? (models.voice_design_loaded ? 'Loaded' : 'Not Loaded') : '--'}
          </div>
        </div>

        <div className="p-md bg-bg-card rounded-md text-center">
          <div className="text-[0.625rem] font-medium text-text-muted uppercase tracking-widest mb-xs">
            Base Model
          </div>
          <div
            className={`font-display text-sm font-semibold ${
              models?.base_loaded ? 'text-accent-cyan' : 'text-text-muted'
            }`}
          >
            {models ? (models.base_loaded ? 'Loaded' : 'Not Loaded') : '--'}
          </div>
        </div>
      </div>

      <Button
        variant="secondary"
        isLoading={isRefreshing}
        onClick={refresh}
        className="w-full"
      >
        {t('refreshStatus')}
      </Button>
    </div>
  );
}
