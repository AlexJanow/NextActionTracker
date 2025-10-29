import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import QueryProvider from './providers/QueryProvider';
import DueActionsDashboard from './components/DueActionsDashboard';
import './index.css';

const App: React.FC = () => {
  return (
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
      </Router>
    </QueryProvider>
  );
};

export default App;