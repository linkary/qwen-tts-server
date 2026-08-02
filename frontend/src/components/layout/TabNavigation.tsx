import { useCallback, useEffect, useLayoutEffect, useRef } from 'react';
import { cn } from '../../utils/cn';
import { useTranslation } from '../../i18n/I18nContext';

export type TabId = 'custom-voice' | 'voice-design' | 'voice-clone' | 'settings';

interface TabNavigationProps {
  activeTab: TabId;
  onTabChange: (tab: TabId) => void;
}

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  const t = useTranslation();
  const navRef = useRef<HTMLElement>(null);
  const indicatorRef = useRef<HTMLSpanElement>(null);
  const isPositioned = useRef(false);

  const tabs: { id: TabId; label: string }[] = [
    { id: 'custom-voice', label: t('customVoice') },
    { id: 'voice-design', label: t('voiceDesign') },
    { id: 'voice-clone', label: t('voiceClone') },
    { id: 'settings', label: t('settings') },
  ];

  /**
   * The indicator's geometry is derived entirely from the active button's layout, so
   * it is written straight to the DOM instead of being held in state: no extra render,
   * and no frame where React's idea of the position disagrees with the measurement.
   */
  const measure = useCallback(() => {
    const indicator = indicatorRef.current;
    const active = navRef.current?.querySelector<HTMLElement>('[data-active="true"]');
    if (!indicator || !active) return;

    // The very first placement must not animate, or the indicator visibly slides in
    // from zero width on load.
    const isFirst = !isPositioned.current;
    if (isFirst) indicator.style.transition = 'none';

    indicator.style.transform = `translate(${active.offsetLeft}px, ${active.offsetTop}px)`;
    indicator.style.width = `${active.offsetWidth}px`;
    indicator.style.height = `${active.offsetHeight}px`;
    indicator.style.opacity = '1';

    if (isFirst) {
      void indicator.offsetWidth; // commit the styles above before re-enabling motion
      indicator.style.transition = '';
      isPositioned.current = true;
    }
  }, []);

  // Measure before paint so the indicator is never seen at a stale position.
  useLayoutEffect(measure, [measure, activeTab, t]);

  // Button widths change after this page's webfont finishes loading and whenever the
  // language switches, either of which would leave the indicator misaligned.
  useEffect(() => {
    const nav = navRef.current;
    if (!nav || typeof ResizeObserver === 'undefined') return;

    const observer = new ResizeObserver(measure);
    nav.querySelectorAll('[role="tab"]').forEach((tab) => observer.observe(tab));
    return () => observer.disconnect();
  }, [measure, tabs.length]);

  return (
    <nav
      ref={navRef}
      className="relative flex gap-xs py-md border-b border-border-subtle mb-xl overflow-x-auto"
      role="tablist"
    >
      {/*
       * The active tab's entire treatment — surface, border and glow — lives on this
       * one element and travels between tabs, instead of fading out on one button
       * while fading in on another. That continuity of position is what reads as
       * deliberate rather than abrupt.
       */}
      <span
        ref={indicatorRef}
        aria-hidden="true"
        className="absolute top-0 left-0 z-0 opacity-0 rounded-md bg-bg-surface border border-accent-cyan shadow-glow-cyan transition-[transform,width,height] duration-[var(--dur-panel,320ms)] ease-[var(--ease-out-expo,cubic-bezier(0.16,1,0.3,1))]"
      />

      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={activeTab === tab.id}
          data-active={activeTab === tab.id}
          onClick={() => onTabChange(tab.id)}
          className={cn(
            'relative z-[1] font-display text-sm font-medium px-lg py-sm rounded-md whitespace-nowrap',
            activeTab === tab.id
              ? 'text-accent-cyan'
              : 'text-text-secondary hover:text-text-primary hover:bg-bg-surface'
          )}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
