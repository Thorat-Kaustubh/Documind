import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';

// PERFORMANCE: Lazy Load non-critical routes (Bundle Size optimization)
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import StockReport from './pages/StockReport';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';

const App: React.FC = () => {
  return (
    <Router>
      <Suspense fallback={
        <div className="min-h-screen bg-[#020617] flex items-center justify-center">
            <div className="w-12 h-12 rounded-full border-4 border-blue-500/20 border-t-blue-500 animate-spin" />
        </div>
      }>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/report/:query" element={
            <ProtectedRoute>
              <StockReport />
            </ProtectedRoute>
          } />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;
