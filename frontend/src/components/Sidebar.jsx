import React from 'react';

const Sidebar = ({ activeSection }) => {
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
      const y = el.getBoundingClientRect().top + window.scrollY - 100;
      window.scrollTo({ top: y, behavior: 'smooth' });
    }
  };

  return (
    <div className="sticky top-24">
      <nav className="space-y-2">
        {sections.map(section => (
          <button
            key={section.id}
            onClick={() => scrollTo(section.id)}
            className={`w-full text-left px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              activeSection === section.id 
                ? 'bg-primary/10 text-primary' 
                : 'text-textMuted hover:text-white hover:bg-surface'
            }`}
          >
            {section.label}
          </button>
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
