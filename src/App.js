import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import LoginSignup from "./component/LoginSignup";

import DashboardLayout from "./component/layout/DashboardLayout";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import PaperTrading from "./pages/PaperTrading";
import AITrading from "./pages/AITrading";
import AccountDetails from "./pages/AccountDetails";
import History from "./pages/History";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/auth" element={<LoginSignup />} />

      {/* DASHBOARD LAYOUT */}
      <Route path="/dashboard" element={<DashboardLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="profile" element={<Profile />} />
        <Route path="paper-trading" element={<PaperTrading />} />
        <Route path="ai-trading" element={<AITrading />} />
        <Route path="account-details" element={<AccountDetails />} />
        <Route path="history" element={<History />} />
      </Route>
    </Routes>
  );
}

export default App;
