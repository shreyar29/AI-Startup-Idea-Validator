import React from 'react';
import { motion } from 'framer-motion';

const SectionSkeleton = () => {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header Skeleton */}
      <div className="flex items-center gap-4 border-b border-white/5 pb-4">
        <div className="w-12 h-12 bg-white/5 rounded-xl"></div>
        <div className="space-y-2">
          <div className="h-6 bg-white/5 rounded w-48"></div>
          <div className="h-4 bg-white/5 rounded w-32"></div>
        </div>
      </div>
      
      {/* Content Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <div className="h-5 bg-white/5 rounded w-1/2 mb-4"></div>
          <div className="space-y-2">
            <div className="h-3 bg-white/5 rounded w-full"></div>
            <div className="h-3 bg-white/5 rounded w-5/6"></div>
            <div className="h-3 bg-white/5 rounded w-4/6"></div>
          </div>
        </div>
        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <div className="h-5 bg-white/5 rounded w-1/3 mb-4"></div>
          <div className="space-y-2">
            <div className="h-3 bg-white/5 rounded w-full"></div>
            <div className="h-3 bg-white/5 rounded w-4/5"></div>
            <div className="h-3 bg-white/5 rounded w-2/3"></div>
          </div>
        </div>
        <div className="glass-panel p-6 rounded-2xl border-white/5 space-y-4">
          <div className="h-5 bg-white/5 rounded w-2/5 mb-4"></div>
          <div className="space-y-2">
            <div className="h-3 bg-white/5 rounded w-full"></div>
            <div className="h-3 bg-white/5 rounded w-11/12"></div>
            <div className="h-3 bg-white/5 rounded w-5/6"></div>
          </div>
        </div>
      </div>
      
      {/* Large Block Skeleton */}
      <div className="glass-panel h-48 rounded-2xl border-white/5 w-full"></div>
    </div>
  );
};

export default SectionSkeleton;
