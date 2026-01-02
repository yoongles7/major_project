// src/pages/LoginSignup.jsx
import React, { useState } from "react";
import Login from "./Login";

const LoginSignup = () => {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow-md w-96 text-center">
        <h2 className="text-2xl font-bold mb-6">
          {isLogin ? "Login" : "Signup"}
        </h2>

        {/* Email/password form placeholder (optional) */}
        {isLogin ? (
          <p className="mb-4">Login with your account or continue with Google</p>
        ) : (
          <p className="mb-4">Signup with your account or continue with Google</p>
        )}

        {/* Google Login Button */}
        <Login />

        <p className="mt-6 text-sm text-gray-600">
          {isLogin ? "Don't have an account?" : "Already have an account?"}{" "}
          <span
            className="text-blue-500 cursor-pointer"
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Signup" : "Login"}
          </span>
        </p>
      </div>
    </div>
  );
};

export default LoginSignup;
