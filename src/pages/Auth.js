import React, { useState } from "react";
import { registerUser, loginUser } from "../services/AuthService";
import { useNavigate } from "react-router-dom";

const Auth = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    password_confirmation: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const saveTokensAndRedirect = (data) => {
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    navigate("/dashboard");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      if (isLogin) {
        // LOGIN
        const response = await loginUser({
          username: formData.username,
          password: formData.password,
        });

        saveTokensAndRedirect(response.data);
      } else {
        // REGISTER

        const response = await registerUser({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          password_confirmation: formData.password_confirmation,
        });
        console.log("Sending data:", {
  username: formData.username,
  email: formData.email,
  password: formData.password,
  password_confirmation: formData.password_confirmation,
});

        saveTokensAndRedirect(response.data);
      }
    } catch (err) {
      if (err.response?.data) {
        const errors = err.response.data;
        setError(JSON.stringify(errors));
      } else {
        setError("Invalid credentials");
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-xl w-96">
        <h2 className="text-3xl font-bold text-white text-center mb-6">
          {isLogin ? "Sign In" : "Create Account"}
        </h2>

        {error && (
          <div className="bg-red-500 text-white p-2 rounded mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Username */}
          <input
            type="text"
            name="username"
            placeholder="Username"
            required
            onChange={handleChange}
            className="w-full p-3 rounded-lg bg-gray-700 text-white outline-none focus:ring-2 focus:ring-blue-500"
          />

          {/* Email only for Register */}
          {!isLogin && (
            <input
              type="email"
              name="email"
              placeholder="Email"
              required
              onChange={handleChange}
              className="w-full p-3 rounded-lg bg-gray-700 text-white outline-none focus:ring-2 focus:ring-blue-500"
            />
          )}

          {/* Password */}
          <input
            type="password"
            name="password"
            placeholder="Password"
            required
            onChange={handleChange}
            className="w-full p-3 rounded-lg bg-gray-700 text-white outline-none focus:ring-2 focus:ring-blue-500"
          />

          {/* Confirm Password only for Register */}
          {!isLogin && (
            <input
              type="password"
              name="password_confirmation"
              placeholder="Confirm Password"
              required
              onChange={handleChange}
              className="w-full p-3 rounded-lg bg-gray-700 text-white outline-none focus:ring-2 focus:ring-blue-500"
            />
          )}

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg font-semibold transition"
          >
            {isLogin ? "Sign In" : "Register"}
          </button>
        </form>

        <p className="text-gray-400 text-center mt-6 text-sm">
          {isLogin ? "Don't have an account?" : "Already have an account?"}
          <span
            onClick={() => {
              setIsLogin(!isLogin);
              setError("");
            }}
            className="text-blue-500 cursor-pointer ml-1"
          >
            {isLogin ? "Register" : "Sign In"}
          </span>
        </p>
      </div>
    </div>
  );
};

export default Auth;