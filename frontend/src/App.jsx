import React, { Suspense, useEffect } from 'react';
import { Routes, Route, useLocation, Link } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import ErrorState from './components/ErrorState';
import VentureLensMascot from './components/Mascot/VentureLensMascot';

const Home = React.lazy(() => import('./pages/Home'));
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Login = React.lazy(() => import('./pages/Login'));
const Signup = React.lazy(() => import('./pages/Signup'));
const History = React.lazy(() => import('./pages/History'));
const VeraWorkspace = React.lazy(() => import('./pages/VeraWorkspace'));

function ScrollToTop() {
  const { pathname } = useLocation();
  
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  
  return null;
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error, errorInfo) {
    // Safe error tracking for future telemetry
    console.error("[ErrorBoundary] React component tree crashed.");
    console.error("Reason:", error?.name || 'Unknown', error?.message);
    
    // Log the component stack trace for diagnostics only in DEV
    if (import.meta.env.DEV) {
      console.debug("[ErrorBoundary] Component Stack:", errorInfo?.componentStack);
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };
  
  render() {
    if (this.state.hasError) {
      return (
        <div className="pt-24 pb-12 flex items-center justify-center">
          <ErrorState 
            message="An unexpected error occurred in the application." 
            onRetry={this.handleRetry} 
          />
        </div>
      );
    }
    return this.props.children;
  }
}

const NotFound = () => (
  <div className="pt-24 pb-12 min-h-[60vh] flex items-center justify-center px-4">
    <div className="text-center">
      <h2 className="text-3xl font-bold text-textMain mb-4">404 - Page Not Found</h2>
      <p className="text-textMuted mb-8">The page you are looking for doesn't exist or has been moved.</p>
      <Link to="/" className="inline-block bg-primary text-white px-6 py-3 rounded-lg font-medium hover:bg-primary/90 transition-colors">
        Return Home
      </Link>
    </div>
  </div>
);

const LoadingFallback = () => (
  <div className="flex items-center justify-center min-h-[60vh]">
    <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
  </div>
);

function App() {
  const location = useLocation();

  return (
    <div className="flex flex-col min-h-screen bg-background text-textMain relative">
      <ScrollToTop />
      <Navbar />
      <main className="flex-grow">
        <ErrorBoundary key={location.pathname}>
          <Suspense fallback={<LoadingFallback />}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/history" element={<History />} />
              <Route path="/vera" element={<VeraWorkspace />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Suspense>
        </ErrorBoundary>
      </main>
      <VentureLensMascot />
      <Footer />
    </div>
  );
}

export default App;
