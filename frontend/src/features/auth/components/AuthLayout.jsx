import React from 'react';

export const AuthLayout = ({ children }) => {
  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 sm:px-6 lg:px-8">
      {children}
    </div>
  );
};
