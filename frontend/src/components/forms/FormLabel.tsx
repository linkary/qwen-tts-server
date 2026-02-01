import React from 'react';

interface FormLabelProps {
  children: React.ReactNode;
  htmlFor?: string;
}

export function FormLabel({ children, htmlFor }: FormLabelProps) {
  return (
    <label
      htmlFor={htmlFor}
      className="block font-display text-xs font-medium text-text-secondary uppercase tracking-widest mb-sm"
    >
      {children}
    </label>
  );
}
