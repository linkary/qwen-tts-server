import React, { TextareaHTMLAttributes, forwardRef, useState, useEffect } from 'react';
import { cn } from '../../utils/cn';

export interface FormTextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  showCounter?: boolean;
}

export const FormTextarea = forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  ({ className, label, showCounter = true, maxLength = 1000, value, onChange, ...props }, ref) => {
    const [count, setCount] = useState(0);

    useEffect(() => {
      if (value !== undefined) {
        setCount(value.toString().length);
      }
    }, [value]);

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      setCount(e.target.value.length);
      onChange?.(e);
    };

    return (
      <div className="w-full">
        {label && (
          <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          className={cn(
            'w-full min-h-[120px] px-md py-md font-body text-base text-text-primary bg-bg-surface border border-border-subtle rounded-md resize-y',
            'transition-all duration-150',
            'focus:outline-none focus:border-accent-cyan focus:shadow-[0_0_0_3px_rgba(0,245,212,0.1)]',
            className
          )}
          maxLength={maxLength}
          value={value}
          onChange={handleChange}
          {...props}
        />
        {showCounter && (
          <div className="font-display text-xs text-text-muted text-right mt-xs">
            {count}/{maxLength}
          </div>
        )}
      </div>
    );
  }
);

FormTextarea.displayName = 'FormTextarea';
