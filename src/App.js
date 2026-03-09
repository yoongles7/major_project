import { Routes, Route, Navigate } from "react-router-dom";

import Home from "./pages/Home";
import Login from "./component/Login";
import Register from "./component/Register";
import DashboardLayout from "./component/layout/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import PaperTrading from "./pages/PaperTrading";
import AITrading from "./pages/AITrading";
import AccountDetails from "./pages/AccountDetails";
import History from "./pages/History";

// Auth check function
const isAuthenticated = () => {
  return !!localStorage.getItem('access_token');
};

// Protected Route component
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

// Public Route component (redirects to dashboard if already logged in)
const PublicRoute = ({ children }) => {
  if (isAuthenticated()) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
};

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<Home />} />
      
      {/* Auth Routes - Public but redirect to dashboard if logged in */}
      <Route path="/login" element={
        <PublicRoute>
          <Login />
        </PublicRoute>
      } />
      <Route path="/register" element={
        <PublicRoute>
          <Register />
        </PublicRoute>
      } />
      
      {/* Legacy auth route - redirect to new login */}
      <Route path="/auth" element={<Navigate to="/login" replace />} />

      {/* Protected Dashboard Routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardLayout />
        </ProtectedRoute>
      }>
        <Route index element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="paper-trading" element={<PaperTrading />} />
        <Route path="ai-trading" element={<AITrading />} />
        <Route path="account-details" element={<AccountDetails />} />
        <Route path="history" element={<History />} />
      </Route>

      {/* Catch all unmatched routes - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default App;