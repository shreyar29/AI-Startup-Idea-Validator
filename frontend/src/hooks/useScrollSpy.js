import { useEffect, useState } from 'react';

export const useScrollSpy = (selectors, options = { rootMargin: '-20% 0px -60% 0px' }, dependencies = []) => {
  const [activeId, setActiveId] = useState('overview');

  useEffect(() => {
    if (dependencies.some(dep => !dep)) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
            window.dispatchEvent(new CustomEvent('sectionChange', { detail: entry.target.id }));
          }
        });
      },
      options
    );

    const elements = document.querySelectorAll(selectors);
    elements.forEach((element) => observer.observe(element));

    return () => observer.disconnect();
  }, dependencies);

  return activeId;
};
