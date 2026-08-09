import React from 'react';

const Sidebar = ({ activeSection }) => {
  const SCROLL_OFFSET_PX = 100;

  const sections = [
    { id: 'overview', label: 'Executive Summary' },
    { id: 'web-search', label: 'Research Evidence' },
    { id: 'market', label: 'Market Intelligence' },
    { id: 'customers', label: 'Customer Intelligence' },
    { id: 'competitors', label: 'Competitive Intelligence' },
    { id: 'comparison', label: 'Final Strategy' }
  ];

  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - SCROLL_OFFSET_PX;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  return (
    <div className="sticky top-24">
      <nav className="space-y-2" aria-label="Dashboard sections">
        {sections.map(section => {
          const isActive = activeSection === section.id;
          return (
            <button
              key={section.id}
              onClick={() => scrollTo(section.id)}
              aria-current={isActive ? 'step' : undefined}
              className={`w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive 
                  ? 'bg-primary/10 text-primary' 
                  : 'text-textMuted hover:text-textMain hover:bg-surface'
              }`}
            >
              {section.label}
            </button>
          );
        })}
      </nav>
    </div>
  );
};

export default Sidebar;
