import React from 'react';

const Footer = () => {
  return (
    <footer className="border-t border-border/50 bg-background/50 py-8 mt-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="text-textMuted text-sm">
          &copy; {new Date().getFullYear()} VentureLens. All rights reserved.
        </div>
        <div className="flex space-x-6 text-sm font-medium text-textMuted">
          <span className="cursor-not-allowed hover:text-textMain transition-colors">Privacy</span>
          <span className="cursor-not-allowed hover:text-textMain transition-colors">Terms</span>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
