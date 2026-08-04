import React from 'react';
import { Rocket, Globe, MessageCircle, Share2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-surface border-t border-white/5 pt-16 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="col-span-1 md:col-span-2">
            <Link to="/" className="flex items-center space-x-2 group mb-4">
              <div className="bg-primary/20 p-2 rounded-xl group-hover:bg-primary/30 transition-colors">
                <Rocket className="h-6 w-6 text-primary" />
              </div>
              <span className="font-bold text-xl tracking-tight text-white">VentureLens</span>
            </Link>
            <p className="text-textMuted max-w-sm mb-6">
              AI-powered startup idea validation. Get market analysis, competitor research, and target audience insights in minutes.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-textMuted hover:text-primary transition-colors"><MessageCircle className="h-5 w-5" /></a>
              <a href="#" className="text-textMuted hover:text-primary transition-colors"><Globe className="h-5 w-5" /></a>
              <a href="#" className="text-textMuted hover:text-primary transition-colors"><Share2 className="h-5 w-5" /></a>
            </div>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Product</h4>
            <ul className="space-y-2">
              <li><Link to="/validate" className="text-textMuted hover:text-white transition-colors">Start Validation</Link></li>
              <li><Link to="/about" className="text-textMuted hover:text-white transition-colors">How it Works</Link></li>
              <li><a href="#" className="text-textMuted hover:text-white transition-colors">Pricing</a></li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-white font-semibold mb-4">Company</h4>
            <ul className="space-y-2">
              <li><Link to="/about" className="text-textMuted hover:text-white transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="text-textMuted hover:text-white transition-colors">Contact</Link></li>
              <li><a href="#" className="text-textMuted hover:text-white transition-colors">Privacy Policy</a></li>
              <li><a href="#" className="text-textMuted hover:text-white transition-colors">Terms of Service</a></li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-textMuted text-sm text-center md:text-left">
            &copy; {new Date().getFullYear()} VentureLens AI. All rights reserved.
          </p>
          <div className="mt-4 md:mt-0 flex space-x-4 text-sm text-textMuted">
            <span>Built with multi-agent AI mesh network</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
