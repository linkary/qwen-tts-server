import React, { useEffect, useRef } from 'react';
import animationStyles from '../../styles/animations.module.css';

interface WaveformVisualizerProps {
  audioElement: HTMLAudioElement | null;
  barCount?: number;
}

export function WaveformVisualizer({ audioElement, barCount = 50 }: WaveformVisualizerProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Generate random bars
    const container = containerRef.current;
    container.innerHTML = '';
    
    for (let i = 0; i < barCount; i++) {
      const bar = document.createElement('div');
      bar.className = animationStyles['waveform-bar'];
      bar.style.height = `${Math.random() * 40 + 10}px`;
      container.appendChild(bar);
    }

    if (!audioElement) return;

    const bars = container.querySelectorAll(`.${animationStyles['waveform-bar']}`);
    let animationFrame: number;

    const animate = () => {
      if (audioElement.paused) {
        bars.forEach(bar => bar.classList.remove(animationStyles.active));
        return;
      }

      bars.forEach((bar) => {
        const height = Math.random() * 50 + 10;
        (bar as HTMLElement).style.height = height + 'px';
        bar.classList.toggle(animationStyles.active, Math.random() > 0.5);
      });

      animationFrame = requestAnimationFrame(animate);
    };

    const handlePlay = () => animate();
    const handlePauseOrEnd = () => {
      cancelAnimationFrame(animationFrame);
      bars.forEach(bar => bar.classList.remove(animationStyles.active));
    };

    audioElement.addEventListener('play', handlePlay);
    audioElement.addEventListener('pause', handlePauseOrEnd);
    audioElement.addEventListener('ended', handlePauseOrEnd);

    return () => {
      cancelAnimationFrame(animationFrame);
      audioElement.removeEventListener('play', handlePlay);
      audioElement.removeEventListener('pause', handlePauseOrEnd);
      audioElement.removeEventListener('ended', handlePauseOrEnd);
    };
  }, [audioElement, barCount]);

  return (
    <div
      ref={containerRef}
      className="h-20 bg-bg-card rounded-md flex items-center justify-center gap-[2px] px-md overflow-hidden mb-md"
    />
  );
}
