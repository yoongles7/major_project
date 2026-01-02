
import React from "react";
import { signInWithPopup } from "firebase/auth";
import { auth, googleprovider } from "../firebase";
import { useNavigate } from "react-router-dom";

const GoogleLoginButton = () => {
  const navigate = useNavigate();

  const handleGoogleLogin = async () => {
 
    try {
      const result = await signInWithPopup(auth, googleprovider);
      console.log("User info:", result.user); // optional
      navigate("/dashboard"); // redirect after login
    } catch (error) {
      console.error("Google login error:", error);
    }
  };

  return (
    <button
      onClick={handleGoogleLogin}
      className="w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded mt-4"
    >
      Continue with Google
    </button>
  );
};

export default GoogleLoginButton;
