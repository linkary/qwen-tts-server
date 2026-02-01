import React from 'react';
import { cn } from '../../utils/cn';

interface StatusIndicatorProps {
  status: 'online' | 'loading' | 'offline';
  text: string;
}

export function StatusIndicator({ status, text }: StatusIndicatorProps) {
  return (
    <div className="flex items-center gap-sm px-md py-sm bg-bg-surface border border-border-subtle rounded-lg">
      <div
        className={cn(
          'w-[10px] h-[10px] rounded-full',
          status === 'online' && 'bg-accent-cyan animate-pulse-glow shadow-[color:var(--tw-shadow-color)]',
          status === 'loading' && 'bg-accent-amber',
          status === 'offline' && 'bg-accent-coral'
        )}
        style={
          status === 'online'
            ? ({ '--tw-shadow-color': '#00f5d4' } as React.CSSProperties)
            : undefined
        }
      />
      <span className="text-sm text-text-secondary">{text}</span>
    </div>
  );
}
