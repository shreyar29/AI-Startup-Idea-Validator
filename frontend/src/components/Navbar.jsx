import React, { useState, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Layers, Sun, Moon, Menu, X, User, LogOut } from 'lucide-react';

const Navbar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState('');

  const [theme, setTheme] = useState(() => {
    return typeof window !== 'undefined' && localStorage.getItem('theme') === 'light' ? 'light' : 'dark';
  });

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      const user = localStorage.getItem('username');
      if (token) {
        setIsAuthenticated(true);
        setUsername(user || 'User');
      } else {
        setIsAuthenticated(false);
        setUsername('');
      }
    };
    checkAuth();
    window.addEventListener('auth-change', checkAuth);
    return () => window.removeEventListener('auth-change', checkAuth);
  }, []);

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      localStorage.theme = 'dark';
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.theme = 'light';
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    localStorage.removeItem('user_id');
    setIsAuthenticated(false);
    window.dispatchEvent(new Event('auth-change'));
    navigate('/');
  };

  const navLinkClass = ({ isActive }) =>
    `transition-colors text-sm font-semibold tracking-wide focus:outline-none focus-visible:text-primary rounded ${
      isActive ? 'text-primary' : 'text-textMuted hover:text-textMain'
    }`;
    
  const mobileNavLinkClass = ({ isActive }) =>
    `block px-3 py-2 rounded-md text-base font-medium transition-colors ${
      isActive ? 'text-primary bg-primary/10' : 'text-textMuted hover:text-textMain hover:bg-surface'
    }`;

  return (
    <nav className="sticky top-0 z-50 w-full glass-panel border-b border-border/50 bg-background/80 backdrop-blur-md">
      <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center gap-3 group focus:outline-none rounded-lg focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background">
            <div className="bg-primary/10 p-1 rounded-xl group-hover:bg-primary/20 transition-all duration-300">
              <img src="/icons/logo.png" alt="VentureLens Logo" className="w-8 h-8 object-cover rounded-lg" />
            </div>
            <span className="font-extrabold text-xl tracking-tight text-textMain">
              Venture<span className="text-primary">Lens</span>
            </span>
          </Link>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            <NavLink to="/" className={navLinkClass}>Home</NavLink>
            <NavLink to="/dashboard" className={navLinkClass}>Dashboard</NavLink>
            {isAuthenticated && <NavLink to="/history" className={navLinkClass}>History</NavLink>}
            
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-textMuted hover:text-textMain transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            
            <div className="flex items-center gap-4 pl-4 border-l border-border/50">
              {isAuthenticated ? (
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm font-semibold text-textMain bg-surface/50 px-3 py-1.5 rounded-full border border-border/50">
                    <User className="w-4 h-4 text-primary" />
                    {username}
                  </div>
                  <button 
                    onClick={handleLogout}
                    className="flex items-center gap-1.5 text-sm font-semibold text-red-400 hover:text-red-300 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Logout
                  </button>
                </div>
              ) : (
                <>
                  <Link 
                    to="/login"
                    className="text-sm font-semibold text-textMuted hover:text-textMain transition-colors"
                  >
                    Log in
                  </Link>
                  <Link 
                    to="/signup"
                    className="px-4 py-2 rounded-lg bg-primary text-background font-bold text-sm hover:bg-primary/90 transition-colors shadow-sm shadow-primary/20"
                  >
                    Sign up
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center gap-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-textMuted hover:text-textMain transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-textMuted hover:text-textMain transition-all duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 focus-visible:ring-offset-background"
              aria-expanded={isMobileMenuOpen}
              aria-label="Toggle navigation menu"
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Panel */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-border/50 bg-background/95 backdrop-blur-md">
          <div className="px-4 pt-2 pb-4 space-y-2">
            <NavLink to="/" onClick={() => setIsMobileMenuOpen(false)} className={mobileNavLinkClass}>Home</NavLink>
            <NavLink to="/dashboard" onClick={() => setIsMobileMenuOpen(false)} className={mobileNavLinkClass}>Dashboard</NavLink>
            {isAuthenticated && <NavLink to="/history" onClick={() => setIsMobileMenuOpen(false)} className={mobileNavLinkClass}>History</NavLink>}
            <div className="pt-4 mt-2 pb-2 border-t border-border/50">
              <div className="flex flex-col gap-3 px-3">
                {isAuthenticated ? (
                  <>
                    <div className="flex items-center gap-2 text-base font-semibold text-textMain justify-center py-2 bg-surface/50 rounded-lg">
                      <User className="w-5 h-5 text-primary" />
                      {username}
                    </div>
                    <button 
                      onClick={() => { handleLogout(); setIsMobileMenuOpen(false); }}
                      className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-red-500/10 text-red-500 font-bold text-base hover:bg-red-500/20 transition-colors"
                    >
                      <LogOut className="w-5 h-5" />
                      Logout
                    </button>
                  </>
                ) : (
                  <>
                    <Link 
                      to="/login" 
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="w-full text-center py-2 text-base font-semibold text-textMuted hover:text-textMain transition-colors"
                    >
                      Log in
                    </Link>
                    <Link 
                      to="/signup" 
                      onClick={() => setIsMobileMenuOpen(false)}
                      className="w-full text-center py-2 rounded-lg bg-primary text-background font-bold text-base hover:bg-primary/90 transition-colors"
                    >
                      Sign up
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
