import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Layers } from 'lucide-react';

const Navbar = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full glass-panel border-b border-border/50 bg-background/80 backdrop-blur-md">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-3 group focus:outline-none rounded-lg focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background">
            <div className="bg-primary/10 p-2 rounded-xl group-hover:bg-primary/20 transition-all duration-300">
              <Layers className="w-5 h-5 text-primary" />
            </div>
            <span className="font-extrabold text-xl tracking-tight text-white">
              Venture<span className="text-primary">Lens</span>
            </span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-8">
            {!isLoggedIn ? (
              <>
                <Link to="/" className="text-textMuted hover:text-white transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded">Home</Link>
                <Link to="/" className="text-textMuted hover:text-white transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded">About</Link>
                <Link to="/" className="text-textMuted hover:text-white transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded">How it Works</Link>
                <Link to="/contact" className="text-textMuted hover:text-white transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded">Contact</Link>
                <button onClick={() => setIsLoggedIn(true)} className="px-5 py-2 rounded-xl bg-white/10 hover:bg-white text-white hover:text-background transition-all duration-300 text-sm font-bold tracking-wide focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background shadow-sm hover:shadow-lg">
                  Sign In
                </button>
              </>
            ) : (
              <>
                <Link to="/" className="text-textMuted hover:text-white transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded">Home</Link>
                <Link to="/" className="text-textMuted hover:text-white transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded">History</Link>
                <Link to="/" className="text-textMuted hover:text-white transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded">Profile</Link>
                <div 
                  onClick={() => setIsLoggedIn(false)}
                  className="w-9 h-9 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary font-bold cursor-pointer hover:bg-primary hover:text-white transition-all duration-300 shadow-sm hover:shadow-primary/50"
                  title="Sign Out"
                >
                  JD
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
