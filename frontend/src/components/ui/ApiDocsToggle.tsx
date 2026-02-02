import { BookOpen } from 'lucide-react';

interface ApiDocsToggleProps {
  isOpen: boolean;
  onClick: () => void;
}

export function ApiDocsToggle({ isOpen, onClick }: ApiDocsToggleProps) {
  return (
    <button
      onClick={onClick}
      className={`fixed top-1/2 -translate-y-1/2 z-[201] bg-gradient-to-b from-accent-cyan to-accent-cyan-dim text-bg-deep border-none rounded-l-md px-sm py-md cursor-pointer font-display text-[0.75rem] font-semibold transition-all duration-300 shadow-glow-cyan hover:px-md hover:shadow-[0_0_24px_rgba(0,245,212,0.4),0_0_48px_rgba(0,245,212,0.2)] ${
        isOpen ? 'right-[600px] hidden md:flex' : 'right-0'
      } flex flex-col items-center gap-sm [writing-mode:vertical-rl]`}
      title="API Documentation"
      style={{ letterSpacing: '0.1em' }}
    >
      <BookOpen className="w-4 h-4 rotate-90" />
      <span>API</span>
    </button>
  );
}
