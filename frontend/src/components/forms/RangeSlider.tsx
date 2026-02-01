import React, { InputHTMLAttributes, forwardRef, useState, useEffect } from 'react';
import { cn } from '../../utils/cn';

export interface RangeSliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  showValue?: boolean;
  formatValue?: (value: number) => string;
}

export const RangeSlider = forwardRef<HTMLInputElement, RangeSliderProps>(
  ({ className, label, showValue = true, formatValue, value, onChange, min = 0.5, max = 2, step = 0.1, ...props }, ref) => {
    const [displayValue, setDisplayValue] = useState(value || 1);

    useEffect(() => {
      if (value !== undefined) {
        setDisplayValue(value);
      }
    }, [value]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setDisplayValue(e.target.value);
      onChange?.(e);
    };

    const formattedValue = formatValue
      ? formatValue(Number(displayValue))
      : `${Number(displayValue).toFixed(1)}x`;

    return (
      <div className="w-full">
        {label && (
          <label className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm">
            {label}
          </label>
        )}
        <div className="flex items-center gap-md">
          {showValue && (
            <span className="font-display text-xs text-text-muted min-w-[3rem]">
              {formatValue ? formatValue(Number(min)) : `${Number(min).toFixed(1)}x`}
            </span>
          )}
          <input
            ref={ref}
            type="range"
            className={cn(
              'flex-1 h-[6px] bg-bg-surface rounded-full outline-none appearance-none',
              '[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-br [&::-webkit-slider-thumb]:from-accent-cyan [&::-webkit-slider-thumb]:to-accent-cyan-dim [&::-webkit-slider-thumb]:cursor-pointer [&::-webkit-slider-thumb]:shadow-[0_0_8px_#00f5d4] [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:hover:scale-110',
              '[&::-moz-range-thumb]:w-5 [&::-moz-range-thumb]:h-5 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-gradient-to-br [&::-moz-range-thumb]:from-accent-cyan [&::-moz-range-thumb]:to-accent-cyan-dim [&::-moz-range-thumb]:cursor-pointer [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:shadow-[0_0_8px_#00f5d4]',
              className
            )}
            min={min}
            max={max}
            step={step}
            value={value}
            onChange={handleChange}
            {...props}
          />
          {showValue && (
            <span className="font-display text-sm font-semibold text-accent-cyan min-w-[3rem] text-right">
              {formattedValue}
            </span>
          )}
        </div>
      </div>
    );
  }
);

RangeSlider.displayName = 'RangeSlider';
