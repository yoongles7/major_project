import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav
      className="fixed top-0 left-0 w-full bg-gray-950 text-white z-50 shadow-lg"
      style={{ fontFamily: "Times New Roman, serif" }}
    >
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link to="/" className="text-xl font-bold">
            StockPredict
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex space-x-8 text-lg">
            <a href="#home" className="hover:text-red-400">Home</a>
            <a href="#about" className="hover:text-red-400">About Us</a>
            <a href="#features" className="hover:text-red-400">Features</a>
            <a href="#contact" className="hover:text-red-400">Contact</a>
          </div>

          {/* Desktop Login / Signup */}
          <div className="hidden md:block">
            <Link
              to="/auth"
              className="px-5 py-1.5 border border-white rounded
                         hover:bg-white hover:text-black transition"
            >
              Login / Signup
            </Link>
          </div>

          {/* Hamburger Icon */}
          <div className="md:hidden">
            <button onClick={() => setIsOpen(!isOpen)}>
              <svg
                className="w-7 h-7"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
          </div>

        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-gray-900 px-6 py-4 space-y-4">
          <a href="#home" className="block">Home</a>
          <a href="#about" className="block">About Us</a>
          <a href="#features" className="block">Features</a>
          <a href="#contact" className="block">Contact</a>

          <Link
            to="/auth"
            className="block text-center mt-4 px-4 py-2
                       border border-white rounded
                       hover:bg-white hover:text-black transition"
          >
            Login / Signup
          </Link>
        </div>
      )}
    </nav>
  );
}
