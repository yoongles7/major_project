import React, { useState } from "react";
import { signOut } from "firebase/auth";
import { auth } from "../../firebase";
import { useNavigate } from "react-router-dom";
import SidebarItem from "./SidebarItem";
import UserPanel from "./UserPanel";
import LogoutModal from "./LogoutModal";

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const navigate = useNavigate();

  const handleLogoutConfirm = async () => {
    try {
      await signOut(auth);
      navigate("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  return (
    <>
      <div
        className={`h-screen bg-gray-100 border-r transition-all duration-300
        ${isCollapsed ? "w-16" : "w-64"} p-4 flex flex-col`}
      >
        {/* Top Section */}
        <div>
          {/* Logo + Collapse */}
          <div className="flex items-center justify-between mb-6">
            {!isCollapsed && <h1 className="text-xl font-bold">LOGO</h1>}
            <button
              onClick={() => setIsCollapsed(!isCollapsed)}
              className="text-gray-600 hover:text-black"
            >
              {isCollapsed ? "➡️" : "⬅️"}
            </button>
          </div>

          {/* User Panel */}
          <UserPanel isCollapsed={isCollapsed} />

          {/* Menu */}
          <div className="space-y-2">
            <SidebarItem label="Dashboard" icon="📊" to="/dashboard" isCollapsed={isCollapsed} />
            <SidebarItem label="Profile" icon="📁" to="/dashboard/profile" isCollapsed={isCollapsed} />
            <SidebarItem label="PaperTrading" icon="💱" to="/dashboard/paper-trading" isCollapsed={isCollapsed} />
            <SidebarItem label="History" icon="🕘" to="/dashboard/history" isCollapsed={isCollapsed} />
            <SidebarItem label="AITrading" icon="🤖" to="/dashboard/ai-trading" isCollapsed={isCollapsed} />
            <SidebarItem label="AccountDetails" icon="⚙️" to="/dashboard/account-details" isCollapsed={isCollapsed} />
          </div>
        </div>

        {/* Bottom Logout */}
        <div className="mt-auto pt-4 border-t">
          <button
            onClick={() => setShowLogoutModal(true)}
            className="w-full flex items-center gap-3 p-3 rounded-lg
                       text-black hover:bg-gray-400"
          >
            <span>⎋</span>
            {!isCollapsed && <span className="text-sm font-medium">Logout</span>}
          </button>
        </div>
      </div>

      {/* Logout Confirmation Modal */}
      {showLogoutModal && (
        <LogoutModal
          onConfirm={handleLogoutConfirm}
          onCancel={() => setShowLogoutModal(false)}
        />
      )}
    </>
  );
};

export default Sidebar;
