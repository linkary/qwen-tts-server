import React, { InputHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../utils/cn';

export interface FormInputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
}

export const FormInput = forwardRef<HTMLInputElement, FormInputProps>(
  ({ className, label, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
            {label}
          </label>
        )}
        <input
          ref={ref}
          className={cn(
            'w-full px-md py-md font-body text-base text-text-primary bg-bg-surface border border-border-subtle rounded-md',
            'transition-all duration-150',
            'focus:outline-none focus:border-accent-cyan focus:shadow-[0_0_0_3px_rgba(0,245,212,0.1)]',
            className
          )}
          {...props}
        />
      </div>
    );
  }
);

FormInput.displayName = 'FormInput';
