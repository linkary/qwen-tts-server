import { BookOpen } from 'lucide-react';
import { cn } from '../../utils/cn';

interface ApiDocsToggleProps {
  isOpen: boolean;
  onClick: () => void;
}

export function ApiDocsToggle({ isOpen, onClick }: ApiDocsToggleProps) {
  return (
    <button
      onClick={onClick}
      // cn() rather than a template string: `hidden` and `flex` both used to be
      // applied at once when open, leaving the winner up to stylesheet order.
      // tailwind-merge resolves the display conflict deterministically.
      className={cn(
        'fixed top-1/2 right-0 -translate-y-1/2 z-[201] flex flex-col items-center gap-sm',
        'bg-gradient-to-b from-accent-cyan to-accent-cyan-dim text-bg-deep border-none',
        'rounded-l-md px-sm py-md cursor-pointer font-display text-[0.75rem] font-semibold',
        'shadow-glow-cyan hover:shadow-[0_0_24px_rgba(0,245,212,0.4),0_0_48px_rgba(0,245,212,0.2)]',
        '[writing-mode:vertical-rl]',
        // Travels with the drawer on `translate` for the same reason the drawer does.
        // The vertical centering above sets --tw-translate-y and the horizontal offset
        // sets --tw-translate-x; Tailwind v4 composes them into one `translate`.
        'transition-transform duration-[var(--dur-panel,320ms)] ease-[var(--ease-out-expo,cubic-bezier(0.16,1,0.3,1))]',
        // On mobile the drawer covers the full width, so there is nowhere to sit.
        isOpen ? 'hidden md:flex md:-translate-x-[600px]' : 'translate-x-0'
      )}
      title="API Documentation"
      style={{ letterSpacing: '0.1em' }}
    >
      <BookOpen className="w-4 h-4 rotate-90" />
      <span>API</span>
    </button>
  );
}
