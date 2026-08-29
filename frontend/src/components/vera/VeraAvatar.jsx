import React from 'react';

export const VeraAvatar = ({ state = 'analyzing', size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-16 h-16',
    lg: 'w-24 h-24 sm:w-32 sm:h-32',
    xl: 'w-32 h-32 sm:w-48 sm:h-48'
  };

  const stateConfig = {
    researching: { color: 'bg-vera-cyan', anim: 'animate-vera-pulse' },
    analyzing: { color: 'bg-vera-cyan', anim: 'animate-vera-spin' },
    confident: { color: 'bg-vera-green', anim: 'opacity-90' },
    celebrating: { color: 'bg-vera-green', anim: 'animate-vera-pulse' },
    cautious: { color: 'bg-vera-amber', anim: 'animate-vera-pulse duration-[3000ms]' },
    critical: { color: 'bg-vera-amber', anim: 'ring-4 ring-vera-amber animate-none' }
  };

  const current = stateConfig[state] || stateConfig.analyzing;

  return (
    <div 
      className={`relative rounded-full bg-vera-shell shadow-2xl flex items-center justify-center animate-vera-hover ${sizeClasses[size]} shrink-0`}
    >
      {/* Dark Glass Faceplate */}
      <div className="absolute inset-1 sm:inset-2 rounded-full bg-vera-glass overflow-hidden flex items-center justify-center shadow-inner">
        {/* Dynamic Iris */}
        <div className={`w-1/2 h-1/2 rounded-full ${current.color} ${current.anim} blur-[2px] shadow-[0_0_15px_currentColor]`} />
      </div>
    </div>
  );
};
