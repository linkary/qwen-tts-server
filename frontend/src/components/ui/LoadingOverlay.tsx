import React from 'react';
import animationStyles from '../../styles/animations.module.css';

export function LoadingOverlay() {
  return (
    <div className="fixed inset-0 bg-bg-deep/90 z-[10000] flex flex-col items-center justify-center">
      <div className="flex items-end justify-center gap-[3px] h-10 p-md">
        <div className={animationStyles['vu-bar']} />
        <div className={animationStyles['vu-bar']} />
        <div className={animationStyles['vu-bar']} />
        <div className={animationStyles['vu-bar']} />
        <div className={animationStyles['vu-bar']} />
      </div>
      <p className="mt-md text-text-secondary font-display">Generating audio...</p>
    </div>
  );
}
