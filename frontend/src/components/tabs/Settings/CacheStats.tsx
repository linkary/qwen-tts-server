import React, { useEffect, useState } from 'react';
import { Button } from '../../ui/Button';
import { useAppContext } from '../../../context/AppContext';
import { useToast } from '../../../context/ToastContext';
import { useTranslation } from '../../../i18n/I18nContext';
import { fetchCacheStats, clearCache } from '../../../services/api';
import type { CacheStatsResponse } from '../../../types/api';

export function CacheStats() {
  const t = useTranslation();
  const { apiKey } = useAppContext();
  const { showToast } = useToast();
  const [stats, setStats] = useState<CacheStatsResponse | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  const refresh = async () => {
    if (!apiKey) return;
    
    setIsRefreshing(true);
    try {
      const data = await fetchCacheStats(apiKey);
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch cache stats:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleClear = async () => {
    if (!apiKey) return;

    setIsClearing(true);
    try {
      await clearCache(apiKey);
      showToast(t('cacheCleared'), 'success');
      await refresh();
    } catch (error) {
      showToast('Failed to clear cache', 'error');
    } finally {
      setIsClearing(false);
    }
  };

  useEffect(() => {
    refresh();
  }, [apiKey]);

  return (
    <div className="p-lg bg-bg-surface border border-border-subtle rounded-lg">
      <h3 className="font-display text-sm font-semibold text-text-primary mb-md flex items-center gap-sm">
        📊 {t('cacheStats')}
      </h3>

      <div>
        <div className="flex justify-between items-center py-sm border-b border-border-subtle">
          <span className="text-sm text-text-secondary">Status</span>
          <span className="font-display font-semibold text-text-primary">
            {stats ? (stats.enabled ? 'Enabled' : 'Disabled') : '--'}
          </span>
        </div>
        <div className="flex justify-between items-center py-sm border-b border-border-subtle">
          <span className="text-sm text-text-secondary">{t('size')}</span>
          <span className="font-display font-semibold text-text-primary">
            {stats ? `${stats.size} / ${stats.max_size}` : '--'}
          </span>
        </div>
        <div className="flex justify-between items-center py-sm border-b border-border-subtle">
          <span className="text-sm text-text-secondary">{t('hitRate')}</span>
          <span className="font-display font-semibold text-text-primary">
            {stats ? `${stats.hit_rate_percent?.toFixed(1) || 0}%` : '--'}
          </span>
        </div>
        <div className="flex justify-between items-center py-sm">
          <span className="text-sm text-text-secondary">{t('requests')}</span>
          <span className="font-display font-semibold text-text-primary">
            {stats ? stats.total_requests || 0 : '--'}
          </span>
        </div>
      </div>

      <div className="flex gap-sm mt-md">
        <Button
          variant="secondary"
          isLoading={isRefreshing}
          onClick={refresh}
          className="flex-1"
        >
          {t('refreshCache')}
        </Button>
        <Button
          variant="danger"
          isLoading={isClearing}
          onClick={handleClear}
          className="flex-1"
        >
          {t('clearCache')}
        </Button>
      </div>
    </div>
  );
}
