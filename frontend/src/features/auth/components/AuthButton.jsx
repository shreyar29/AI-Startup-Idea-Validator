import React from 'react';
import { Loader2 } from 'lucide-react';

export const AuthButton = ({ children, isLoading, type = 'submit', ...props }) => {
  return (
    <button 
      type={type} 
      disabled={isLoading}
      className={`w-full flex items-center justify-center bg-primary hover:bg-primary/90 text-background font-bold py-3.5 rounded-xl transition-all shadow-md hover:shadow-primary/20 ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
      aria-disabled={isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <Loader2 className="w-5 h-5 mr-2 animate-spin" aria-hidden="true" />
          Processing...
        </>
      ) : (
        children
      )}
    </button>
  );
};
