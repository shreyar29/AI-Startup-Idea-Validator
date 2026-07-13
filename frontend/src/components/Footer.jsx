const Footer = () => {
  return (
    <footer className="border-t border-white/10 bg-background/50 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="font-semibold text-lg text-white">VentureLens</span>
            <span className="text-sm text-textMuted">— AI Startup Idea Validator</span>
          </div>
          <p className="mt-4 md:mt-0 text-sm text-textMuted">
            &copy; {new Date().getFullYear()} VentureLens. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
