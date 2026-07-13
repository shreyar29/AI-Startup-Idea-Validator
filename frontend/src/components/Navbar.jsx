import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Rocket, Activity } from 'lucide-react';

const Navbar = () => {
  const location = useLocation();

  const navLinks = [
    { name: 'Home', path: '/', icon: Rocket },
    { name: 'Validate', path: '/validate', icon: Activity },
  ];

  return (
    <nav className="fixed top-0 w-full z-50 glass-panel border-b-0 border-white/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <Rocket className="w-6 h-6 text-primary" />
            <span className="font-bold text-xl tracking-tight text-white">VentureLens</span>
          </Link>
          <div className="hidden md:block">
            <div className="flex items-baseline space-x-1">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = location.pathname === link.path;
                return (
                  <Link
                    key={link.name}
                    to={link.path}
                    className={`relative px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                      isActive ? 'text-white' : 'text-textMuted hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <div className="flex items-center space-x-1.5">
                      <Icon className="w-4 h-4" />
                      <span>{link.name}</span>
                    </div>
                    {isActive && (
                      <motion.div
                        layoutId="navbar-indicator"
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                      />
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
