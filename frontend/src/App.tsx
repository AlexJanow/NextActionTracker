import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QueryProvider from './providers/QueryProvider';
import { TenantProvider } from './contexts/TenantContext';
import { ToastProvider } from './contexts/ToastContext';
import { ThemeProvider } from './contexts/ThemeContext';
import DueActionsDashboard from './components/DueActionsDashboard';
import ToastContainer from './components/ToastContainer';
import ErrorBoundary from './components/ErrorBoundary';
import ThemeToggle from './components/ThemeToggle';
import './index.css';

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <TenantProvider>
          <ToastProvider>
            <QueryProvider>
              <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                <div className="container">
                  <header className="header">
                    <div>
                      <h1>Nächste Aktionen</h1>
                      <p>Behalten Sie Ihre Sales-Pipeline im Blick – kein Deal bleibt liegen</p>
                    </div>
                    <ThemeToggle />
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
      </ThemeProvider>
    </ErrorBoundary>
  );
};

export default App;