import React from 'react';
import { cn } from '../../utils/cn';

export interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label?: string;
}

export function Toggle({ checked, onChange, label }: ToggleProps) {
  return (
    <div className="flex items-center gap-md">
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={cn(
          'relative w-12 h-6 rounded-full border transition-all duration-150 cursor-pointer',
          checked
            ? 'bg-accent-cyan border-accent-cyan'
            : 'bg-bg-surface border-border-subtle'
        )}
      >
        <span
          className={cn(
            'absolute top-[2px] w-[18px] h-[18px] rounded-full transition-all duration-150',
            checked
              ? 'left-[22px] bg-bg-deep'
              : 'left-[2px] bg-text-primary'
          )}
        />
      </button>
      {label && <span className="text-sm text-text-secondary">{label}</span>}
    </div>
  );
}
