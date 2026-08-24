import React from 'react';
import { Link } from 'react-router-dom';
import { AuthLayout } from '../features/auth/components/AuthLayout';
import { AuthCard } from '../features/auth/components/AuthCard';

const Signup = () => {
  return (
    <AuthLayout>
      <AuthCard 
        title="Coming Soon" 
        subtitle="Registration is currently closed."
      >
        <div className="flex flex-col items-center justify-center py-8 space-y-6">
          <p className="text-textMuted text-center">
            We are working hard to bring you enterprise-grade user accounts and project management. Check back soon!
          </p>
          <Link to="/" className="px-6 py-3 rounded-lg bg-primary text-background font-bold text-sm hover:bg-primary/90 transition-colors shadow-sm">
            Return to Homepage
          </Link>
        </div>
      </AuthCard>
    </AuthLayout>
  );
};

export default Signup;
