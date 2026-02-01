import React, { SelectHTMLAttributes, forwardRef } from 'react';
import { cn } from '../../utils/cn';

export interface FormSelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
}

export const FormSelect = forwardRef<HTMLSelectElement, FormSelectProps>(
  ({ className, label, children, ...props }, ref) => {
    return (
      <div className="w-full">
        {label && (
          <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={cn(
            'w-full px-md py-md pr-10 font-body text-base text-text-primary bg-bg-surface border border-border-subtle rounded-md cursor-pointer appearance-none',
            'transition-all duration-150',
            'focus:outline-none focus:border-accent-cyan focus:shadow-[0_0_0_3px_rgba(0,245,212,0.1)]',
            'bg-[url("data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'16\' height=\'16\' viewBox=\'0 0 24 24\' fill=\'none\' stroke=\'%239090a0\' stroke-width=\'2\'%3E%3Cpath d=\'M6 9l6 6 6-6\'/%3E%3C/svg%3E")] bg-no-repeat bg-[right_12px_center]',
            className
          )}
          {...props}
        >
          {children}
        </select>
      </div>
    );
  }
);

FormSelect.displayName = 'FormSelect';
