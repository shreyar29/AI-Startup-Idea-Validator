import React from 'react';
import { VeraAvatar } from './VeraAvatar';

export const VeraHero = ({ inputValue }) => {
  // If user is typing, Vera is 'researching'
  const state = (inputValue && inputValue.length > 10) ? 'researching' : 'confident';
  
  return (
    <div className="flex flex-col items-center gap-4">
      <VeraAvatar state={state} size="xl" />
      <p className="text-vera-cyan font-mono text-xs sm:text-sm tracking-widest h-5 transition-opacity duration-300">
        {(inputValue && inputValue.length > 10) ? "Vera is analyzing your input..." : "Vera is ready."}
      </p>
    </div>
  );
};
