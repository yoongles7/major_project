// src/components/sidebar/UserPanel.jsx
import React from "react";

const UserPanel = ({ isCollapsed }) => {
  return (
    <div className="border-b pb-4 mb-4">
      {!isCollapsed ? (
        <>
          <p className="text-lg font-semibold">StockPredict</p>
          <p className="text-sm text-gray-600">Welcome back...</p>
        </>
      ) : (
        <div className="w-8 h-8 bg-gray-300 rounded-full mx-auto" />
      )}
    </div>
  );
};

export default UserPanel;
