import React from 'react';
import { useToast } from '../../context/ToastContext';
import { cn } from '../../utils/cn';

export function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed bottom-lg right-lg z-[1000] flex flex-col gap-sm">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={cn(
            'px-lg py-md bg-bg-elevated border rounded-md shadow-card text-sm text-text-primary',
            'flex items-center gap-md animate-slideInRight',
            toast.type === 'success' && 'border-accent-cyan',
            toast.type === 'error' && 'border-accent-coral',
            toast.type === 'warning' && 'border-accent-amber',
            toast.type === 'info' && 'border-border-subtle'
          )}
          onClick={() => removeToast(toast.id)}
        >
          {toast.message}
        </div>
      ))}
    </div>
  );
}
