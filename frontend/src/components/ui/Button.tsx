import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../utils/cn';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  isLoading?: boolean;
  loadingText?: string;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', isLoading, loadingText, children, disabled, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center gap-2 px-xl py-md font-display text-sm font-semibold uppercase tracking-wider rounded-md transition-all duration-150 disabled:cursor-not-allowed';

    const variantStyles = {
      primary:
        'bg-gradient-to-br from-accent-cyan to-accent-cyan-dim text-bg-deep shadow-glow-cyan hover:translate-y-[-2px] hover:shadow-[0_0_24px_rgba(0,245,212,0.4),0_0_48px_rgba(0,245,212,0.2)] active:translate-y-0',
      secondary:
        'bg-bg-surface text-text-primary border border-border-subtle hover:bg-bg-elevated hover:border-border-active',
      danger:
        'bg-gradient-to-br from-accent-coral to-accent-coral-dim text-bg-deep hover:shadow-glow-coral',
    };

    const spinnerColor = {
      primary: 'border-t-bg-deep',
      secondary: 'border-t-accent-cyan',
      danger: 'border-t-bg-deep',
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variantStyles[variant],
          isLoading && 'pointer-events-none opacity-80',
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <span className={cn('w-5 h-5 border-2 border-transparent rounded-full animate-spin', spinnerColor[variant])} />
            <span>{loadingText || 'Generating...'}</span>
          </>
        ) : (
          children
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';
