import React from 'react';
import type { AudioMetrics } from '../../types/audio';

interface PerformanceMetricsProps {
  metrics: AudioMetrics;
  showCache?: boolean;
}

export function PerformanceMetrics({ metrics, showCache = false }: PerformanceMetricsProps) {
  return (
    <div className="flex gap-lg mt-md pt-md border-t border-border-subtle flex-wrap">
      <div className="flex flex-col gap-xs">
        <span className="text-[0.625rem] font-medium text-text-muted uppercase tracking-widest">
          Generation Time
        </span>
        <span className="font-display text-base font-bold text-accent-cyan">
          {metrics.generationTime?.toFixed(2) || '--'}s
        </span>
      </div>
      
      <div className="flex flex-col gap-xs">
        <span className="text-[0.625rem] font-medium text-text-muted uppercase tracking-widest">
          Audio Duration
        </span>
        <span className="font-display text-base font-bold text-accent-cyan">
          {metrics.audioDuration?.toFixed(2) || '--'}s
        </span>
      </div>
      
      <div className="flex flex-col gap-xs">
        <span className="text-[0.625rem] font-medium text-text-muted uppercase tracking-widest">
          RTF
        </span>
        <span className="font-display text-base font-bold text-accent-cyan">
          {metrics.rtf?.toFixed(2) || '--'}x
        </span>
      </div>
      
      {showCache && metrics.cacheStatus && (
        <div className="flex flex-col gap-xs">
          <span className="text-[0.625rem] font-medium text-text-muted uppercase tracking-widest">
            Cache
          </span>
          <span className="font-display text-base font-bold text-accent-cyan">
            {metrics.cacheStatus}
          </span>
        </div>
      )}
    </div>
  );
}
