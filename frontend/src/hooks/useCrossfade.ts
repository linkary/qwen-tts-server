import { useCallback, useEffect, useState } from 'react';
import type { AnimationEvent } from 'react';

/**
 * Upper bound for waiting on an `animationend` event.
 *
 * Deliberately far longer than any real animation: this is a stall guard, not a timing
 * source. It only matters if no animation runs at all — e.g. the browser has animations
 * switched off, or the element is hidden mid-transition — in which case `animationend`
 * never arrives and a state machine driven by it would hang.
 */
const ANIMATION_FALLBACK_MS = 600;

export type CrossfadePhase = 'idle' | 'leaving' | 'entering';

export interface Crossfade<T> {
  /**
   * The value that should actually be rendered. It lags `value` by one exit animation
   * so the outgoing content can animate away before being replaced.
   */
  rendered: T;
  phase: CrossfadePhase;
  /** Attach to the animating element, alongside `key={rendered}`. */
  onAnimationEnd: (event: AnimationEvent<Element>) => void;
}

/**
 * Drives a wait-mode crossfade for a value that swaps (a tab id, a mode, ...).
 *
 * A plain CSS `animation` class cannot do this alone: the element wrapping the content
 * is not remounted when the value changes, so the animation never replays, and CSS has
 * no way to hold the old content on screen while it leaves.
 *
 * All timing is owned by the stylesheet — phases advance on `animationend`, and the
 * durations live as `--dur-*` custom properties in `src/styles/globals.css`. That also
 * covers `prefers-reduced-motion` for free: the media query there collapses durations
 * to 1ms, so the sequence still completes, just imperceptibly fast.
 */
export function useCrossfade<T>(value: T): Crossfade<T> {
  const [rendered, setRendered] = useState<T>(value);
  const [phase, setPhase] = useState<CrossfadePhase>('idle');
  const [previous, setPrevious] = useState<T>(value);

  // Adjusted during render rather than in an effect: React re-runs this component
  // immediately, before touching the DOM, so the outgoing content is marked as leaving
  // in the very commit the new value arrives in — no wasted frame showing it as idle.
  // https://react.dev/learn/you-might-not-need-an-effect
  if (value !== previous) {
    setPrevious(value);
    setPhase('leaving');
  }

  // Closes over the current `value` rather than tracking it in a ref: React re-attaches
  // the handler below on every render and the guard timer is re-armed alongside it, so
  // clicking through several tabs while one is still leaving lands on the tab the user
  // actually ended up on.
  const advance = useCallback(() => {
    if (phase === 'leaving') {
      setRendered(value);
      setPhase('entering');
    } else if (phase === 'entering') {
      setPhase('idle');
    }
  }, [phase, value]);

  useEffect(() => {
    if (phase === 'idle') return;
    const timer = setTimeout(advance, ANIMATION_FALLBACK_MS);
    return () => clearTimeout(timer);
  }, [phase, advance]);

  const onAnimationEnd = useCallback(
    (event: AnimationEvent<Element>) => {
      // Animations on descendants (the audio player's slide-up, for one) bubble through
      // this handler — only the wrapper's own animation should advance the sequence.
      if (event.target !== event.currentTarget) return;
      advance();
    },
    [advance]
  );

  return { rendered, phase, onAnimationEnd };
}
