import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../utils/cn';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  isLoading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', isLoading, children, disabled, ...props }, ref) => {
    const baseStyles =
      'inline-flex items-center justify-center gap-2 px-xl py-md font-display text-sm font-semibold uppercase tracking-wider rounded-md transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed';

    const variantStyles = {
      primary:
        'bg-gradient-to-br from-accent-cyan to-accent-cyan-dim text-bg-deep shadow-glow-cyan hover:translate-y-[-2px] hover:shadow-[0_0_24px_rgba(0,245,212,0.4),0_0_48px_rgba(0,245,212,0.2)] active:translate-y-0',
      secondary:
        'bg-bg-surface text-text-primary border border-border-subtle hover:bg-bg-elevated hover:border-border-active',
      danger:
        'bg-gradient-to-br from-accent-coral to-accent-coral-dim text-bg-deep hover:shadow-glow-coral',
    };

    return (
      <button
        ref={ref}
        className={cn(
          baseStyles,
          variantStyles[variant],
          isLoading && 'relative text-transparent',
          className
        )}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <span className="absolute inset-0 flex items-center justify-center">
            <span className="w-5 h-5 border-2 border-transparent border-t-current rounded-full animate-spin" />
          </span>
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
