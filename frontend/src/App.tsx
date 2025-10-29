import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QueryProvider from './providers/QueryProvider';
import { TenantProvider } from './contexts/TenantContext';
import { ToastProvider } from './contexts/ToastContext';
import DueActionsDashboard from './components/DueActionsDashboard';
import ToastContainer from './components/ToastContainer';
import ErrorBoundary from './components/ErrorBoundary';
import './index.css';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <TenantProvider>
        <ToastProvider>
          <QueryProvider>
            <Router>
              <div className="container">
                <header className="header">
                  <h1>Next Action Tracker</h1>
                  <p>Stay on top of your sales pipeline - never let a deal go cold</p>
                </header>
                
                <main>
                  <Routes>
                    <Route path="/" element={<DueActionsDashboard />} />
                  </Routes>
                </main>
              </div>
              <ToastContainer />
            </Router>
          </QueryProvider>
        </ToastProvider>
      </TenantProvider>
    </ErrorBoundary>
  );
};

export default App;