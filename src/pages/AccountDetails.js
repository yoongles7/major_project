import React, { useEffect, useState } from "react";
import { getAuth, updateProfile } from "firebase/auth"; // Firebase must be initialized

export default function AccountDetails() {
  const auth = getAuth();
  const [user, setUser] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editData, setEditData] = useState({
    fullName: "",
    country: "",
    accountType: "",
    kycStatus: "",
    brokerName: "",
  });

  useEffect(() => {
    const currentUser = auth.currentUser;

    if (currentUser) {
      setUser({
        fullName: currentUser.displayName || "User",
        email: currentUser.email,
        joinedDate: currentUser.metadata.creationTime
          ? new Date(currentUser.metadata.creationTime).toLocaleDateString()
          : "N/A",
        lastLogin: currentUser.metadata.lastSignInTime
          ? new Date(currentUser.metadata.lastSignInTime).toLocaleString()
          : "N/A",
        status: currentUser.emailVerified ? "Active" : "Pending Verification",
        role: "Trader",
        accountType: "Paper Trading",
        country: "Nepal",
        kycStatus: "Pending",
        brokerName: "N/A",
        loginHistory: ["2026-01-03 16:00", "2026-01-02 14:20", "2026-01-01 18:45"],
      });
    }
  }, [auth]);

  if (!user) {
    return (
      <div className="p-6 text-gray-500 text-center">Loading account details...</div>
    );
  }

  const openModal = () => {
    setEditData({
      fullName: user.fullName,
      country: user.country,
      accountType: user.accountType,
      kycStatus: user.kycStatus,
      brokerName: user.brokerName,
    });
    setIsModalOpen(true);
  };

  const handleChange = (e) => {
    setEditData({ ...editData, [e.target.name]: e.target.value });
  };

  const handleSave = async () => {
    try {
      if (auth.currentUser) {
        await updateProfile(auth.currentUser, {
          displayName: editData.fullName,
        });
        setUser({
          ...user,
          fullName: editData.fullName,
          country: editData.country,
          accountType: editData.accountType,
          kycStatus: editData.kycStatus,
          brokerName: editData.brokerName,
        });
        setIsModalOpen(false);
      }
    } catch (err) {
      console.error("Error updating profile:", err);
    }
  };

  return (
    <div className="p-6 space-y-6 bg-gray-300">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-serif font-bold text-gray-900">ACCOUNT DETAILS</h1>
        <p className="text-sm text-gray-700">
          Manage your personal information and account settings
        </p>
      </div>

      {/* Profile Card */}
      <div className="bg-gray-100 rounded-lg shadow p-6 flex items-center gap-6">
        <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center text-5xl font-bold text-blue-500">
          {user.fullName.charAt(0)}
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-800">{user.fullName}</h2>
          <p className="text-gray-500">{user.email}</p>
          <span className="inline-block mt-2 px-3 py-1 text-xs rounded-full bg-green-100 text-green-700">
            {user.status}
          </span>
        </div>
        <button
          onClick={openModal}
          className="ml-auto px-4 py-2 rounded-md bg-yellow-500 text-white text-sm hover:bg-yellow-600 transition"
        >
          ✏️ Edit Profile
        </button>
      </div>

      {/* Account Info */}
      <div className="bg-gray-100 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-900">Account Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-medium">
          <Detail label="Full Name" value={user.fullName} />
          <Detail label="Email Address" value={user.email} />
          <Detail label="Account Type" value={user.accountType} />
          <Detail label="Role" value={user.role} />
          <Detail label="Country" value={user.country} />
          <Detail label="Joined Date" value={user.joinedDate} />
          <Detail label="Last Login" value={user.lastLogin} />
        </div>
      </div>

      {/* Security */}
      <div className="bg-gray-100 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">Security</h3>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <p className="text-sm text-gray-500">
            Keep your account secure by updating your password regularly.
          </p>
          <button className="px-4 py-2 rounded-md bg-blue-600 text-white text-sm hover:bg-blue-700 transition">
            Change Password
          </button>
        </div>
      </div>

      {/* KYC / Broker Details */}
      <div className="bg-gray-100 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">🧾 KYC & Broker Details</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <Detail label="KYC Status" value={user.kycStatus} />
          <Detail label="Broker Name" value={user.brokerName} />
        </div>
      </div>

      {/* Login History */}
      <div className="bg-gray-100 rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4 text-gray-800">🕒 Login History</h3>
        {user.loginHistory?.length === 0 ? (
          <p className="text-gray-500 text-sm">No login records found.</p>
        ) : (
          <ul className="list-disc list-inside text-sm text-gray-700">
            {user.loginHistory?.map((login, index) => (
              <li key={index}>{login}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Edit Profile Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg w-11/12 max-w-md p-6 relative">
            <h2 className="text-xl font-semibold mb-4">Edit Profile</h2>

            <div className="space-y-4">
              {/* Full Name */}
              <div>
                <label className="block text-gray-500 text-sm mb-1">Full Name</label>
                <input
                  type="text"
                  name="fullName"
                  value={editData.fullName}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>

              {/* Country */}
              <div>
                <label className="block text-gray-500 text-sm mb-1">Country</label>
                <input
                  type="text"
                  name="country"
                  value={editData.country}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>

              {/* Account Type */}
              <div>
                <label className="block text-gray-500 text-sm mb-1">Account Type</label>
                <select
                  name="accountType"
                  value={editData.accountType}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                  <option>Paper Trading</option>
                  <option>Live Trading</option>
                  <option>Custom</option>
                </select>
              </div>

              {/* KYC Status */}
              <div>
                <label className="block text-gray-500 text-sm mb-1">KYC Status</label>
                <select
                  name="kycStatus"
                  value={editData.kycStatus}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                >
                  <option>Pending</option>
                  <option>Verified</option>
                  <option>Rejected</option>
                </select>
              </div>

              {/* Broker Name */}
              <div>
                <label className="block text-gray-500 text-sm mb-1">Broker Name</label>
                <input
                  type="text"
                  name="brokerName"
                  value={editData.brokerName}
                  onChange={handleChange}
                  className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 rounded-md bg-gray-300 text-gray-700 hover:bg-gray-400 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="px-4 py-2 rounded-md bg-blue-600 text-white hover:bg-blue-700 transition"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Reusable detail row
function Detail({ label, value }) {
  return (
    <div className="flex flex-col">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-800">{value}</span>
    </div>
  );
}
