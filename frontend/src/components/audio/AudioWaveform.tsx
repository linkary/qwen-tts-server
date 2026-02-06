import React, { useEffect, useRef } from 'react';
import { cn } from '../../utils/cn';

interface AudioWaveformProps {
  mode: 'playback' | 'recording';
  audioElement?: HTMLAudioElement | null;
  mediaStream?: MediaStream | null;
  isActive?: boolean;
  barCount?: number;
  height?: number;
  className?: string;
  barColor?: string;
}

// Helper to dim header colors for gradient bottom
function adjustColorOpacity(hex: string, opacity: number) {
  // Basic hex to rgba
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

export function AudioWaveform({
  mode,
  audioElement,
  mediaStream,
  isActive = false,
  barCount = 64,
  height = 80,
  className,
  barColor = '#00f5d4' // accent-cyan
}: AudioWaveformProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>(undefined);
  const analyserRef = useRef<AnalyserNode>(undefined);
  const audioContextRef = useRef<AudioContext>(undefined);
  const sourceRef = useRef<MediaElementAudioSourceNode | MediaStreamAudioSourceNode>(undefined);

  useEffect(() => {
    // Cleanup previous context if any
    return () => {
      if (animationRef.current !== undefined) {
        cancelAnimationFrame(animationRef.current);
      }
      if (sourceRef.current) {
        sourceRef.current.disconnect();
      }
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    const initAudioContext = async () => {
      // Don't initialize if conditions aren't met
      if (!isActive && mode === 'playback' && audioElement?.paused) return;
      if (!isActive && mode === 'recording' && !mediaStream) return;

      // Initialize AudioContext if not exists
      if (!audioContextRef.current || audioContextRef.current.state === 'closed') {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      const ctx = audioContextRef.current;
      
      // Create Analyser
      if (!analyserRef.current) {
        analyserRef.current = ctx.createAnalyser();
        analyserRef.current.fftSize = 256;
        analyserRef.current.smoothingTimeConstant = 0.5;
      }
      
      const analyser = analyserRef.current;

      // Handle Source Connection
      // Note: We avoid reconnecting if the source is already set up and valid for the current mode
      // However, simplified approach: disconnect old source if any, creates new one
      if (sourceRef.current) {
        try {
          sourceRef.current.disconnect();
        } catch (_) { /* ignore */ }
      }

      try {
        if (mode === 'playback' && audioElement) {
          // Connect audio element
          // We check a custom property or try-catch because createMediaElementSource can throw if already connected
          if (!(audioElement as any).__audioSourceNode) {
             const source = ctx.createMediaElementSource(audioElement);
             source.connect(analyser);
             analyser.connect(ctx.destination);
             sourceRef.current = source;
             (audioElement as any).__audioSourceNode = source;
          } else {
             sourceRef.current = (audioElement as any).__audioSourceNode;
             // Ensure it's connected to our current analyser
             sourceRef.current?.connect(analyser);
             // Ensure analyser is connected to destination
             analyser.connect(ctx.destination);
          }
        } else if (mode === 'recording' && mediaStream) {
          // Connect microphone stream
          const source = ctx.createMediaStreamSource(mediaStream);
          source.connect(analyser);
          sourceRef.current = source;
        }
      } catch (err) {
        console.warn('Audio visualization source connection error:', err);
      }

      // Start Animation
      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      const canvas = canvasRef.current;
      
      if (!canvas) return;

      const canvasCtx = canvas.getContext('2d');
      if (!canvasCtx) return;

      // Setup canvas scaling for retina displays
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      canvasCtx.scale(dpr, dpr);

      const draw = () => {
        if (!isActive && mode === 'recording') {
           // Clear canvas if recording stopped
           canvasCtx.clearRect(0, 0, rect.width, rect.height);
           // Draw flat line
           canvasCtx.fillStyle = 'rgba(255, 255, 255, 0.1)';
           for (let i = 0; i < barCount; i++) {
             const barWidth = (rect.width / barCount) * 0.8;
             const x = i * (rect.width / barCount);
             canvasCtx.fillRect(x, rect.height / 2 - 1, barWidth, 2);
           }
           return;
        }

        animationRef.current = requestAnimationFrame(draw);
        analyser.getByteFrequencyData(dataArray);

        canvasCtx.clearRect(0, 0, rect.width, rect.height);

        // Custom visualization logic
        // We stretch the frequency data to fit our bar count
        const step = Math.floor(bufferLength / barCount);
        let x = 0;

        for (let i = 0; i < barCount; i++) {
          const dataIndex = Math.min(i * step, bufferLength - 1);
          const value = dataArray[dataIndex];
          
          // Normalized height (0-1)
          const percent = value / 255;
          
          // Add some minimum height so bars are always visible
          const barH = Math.max(4, percent * rect.height * 0.8);
          
          // Center vertically
          const y = (rect.height - barH) / 2;

          // Gradient color based on height/intensity
          const gradient = canvasCtx.createLinearGradient(0, y, 0, y + barH);
          gradient.addColorStop(0, barColor);
          gradient.addColorStop(1, adjustColorOpacity(barColor, 0.3));

          canvasCtx.fillStyle = isActive || value > 0 ? gradient : 'rgba(255, 255, 255, 0.1)';
          
          // Enhanced visual for idle state
          if (!isActive && value === 0) {
              const barWidth = (rect.width / barCount) * 0.8;
              canvasCtx.fillRect(x, rect.height / 2 - 1, barWidth, 2);
          } else {
              const barWidth = (rect.width / barCount) * 0.8;
              canvasCtx.fillRect(x, y, barWidth, barH);
          }

          x += rect.width / barCount;
        }
      };

      draw();
    };

    if (isActive) {
       initAudioContext();
    } else if (animationRef.current !== undefined) {
       cancelAnimationFrame(animationRef.current);
       animationRef.current = undefined;
       // Draw one last frame to clear or set idle state
       const canvas = canvasRef.current;
       if (canvas) {
         const ctx = canvas.getContext('2d');
         const rect = canvas.getBoundingClientRect();
         if (ctx) {
            ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
            const dpr = window.devicePixelRatio || 1;
            ctx.clearRect(0, 0, canvas.width / dpr, canvas.height / dpr);
            
            // Draw idle line
             for (let i = 0; i < barCount; i++) {
               const barWidth = (rect.width / barCount) * 0.8;
               const x = i * (rect.width / barCount);
               ctx.fillRect(x, rect.height / 2 - 1, barWidth, 2);
             }
         }
       }
    }
  }, [isActive, mode, audioElement, mediaStream, barCount, barColor]);

  return (
    <div className={cn("relative w-full bg-bg-card rounded-md overflow-hidden", className)} style={{ height }}>
      <canvas 
        ref={canvasRef}
        className="w-full h-full"
      />
    </div>
  );
}
